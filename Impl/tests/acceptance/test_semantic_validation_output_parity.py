"""BUG-4 and AT-PARSER-007-03 through the CLI entry point."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
MODES = [
    (),
    ("--ast-sem",),
    ("--ast-sem", "--json"),
    ("--ast-sem", "--ast-output", "ast.json"),
    ("--ast-sem", "--ast-combine"),
]
INVALID_STEP = '    1. VALIDATE value AS TYPE.String @format("email") AS CHECK_FORMAT'
SCOPE_ERROR = "Annotation @format is not allowed in scope STEP"


def write_spec(directory, filename, body, version="1.2"):
    source = directory / filename
    source.write_text(f'VERSION {version}\nCONTEXT: "Validation parity"\nTARGET: "Python3"\n{body}', encoding="utf-8")
    return source


def run_cli(source, *flags):
    return subprocess.run(
        [sys.executable, "-m", "Impl.cli", *flags, source.name],
        cwd=source.parent, env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True, text=True, timeout=30,
    )


def assert_annotation_error(result, source, flags, message, line, column):
    assert result.returncode == 1, result.stderr
    assert result.stdout == ""
    assert result.stderr.count(message) == 1, result.stderr
    if "--json" in flags:
        report = json.loads(result.stderr)
        assert report["success"] is False
        assert report["semantic_validate"]["status"] == "FAILED"
        assert "semantic_ast_sha512" not in report
        matching_errors = [
            (item["sourceFile"], error["location"]["line"], error["location"]["column"])
            for item in report["reports"] for error in item["errors"]
            if error["message"] == message
        ]
        assert matching_errors == [(source.name, line, column)]
    else:
        assert f"{source.resolve()}:{line}:{column}" in result.stderr


@pytest.mark.parametrize("flags", MODES)
def test_valid_annotations_in_all_output_modes(tmp_path, flags):
    source = write_spec(tmp_path, "valid.gasd", '''\
NAMESPACE: "parity"
TYPE Input:
    value: String @format("email") AS INPUT_FORMAT
FLOW check(value: Input):
    1. VALIDATE value AS TYPE.Input @constraint("Value exists") AS CHECK_INPUT
''')
    result = run_cli(source, *flags)
    assert result.returncode == 0, result.stderr
    if "--ast-output" in flags:
        assert result.stdout == ""
        payload = (tmp_path / "ast.json").read_text(encoding="utf-8")
    elif "--json" in flags or "--ast-combine" in flags:
        payload = result.stdout
    else:
        assert result.stdout == ""
        return

    ast = json.loads(payload)
    assert ast["semantic_validate"]["status"] == "PASSED"
    scopes = {}
    for occurrence in ast["source_inventory"]:
        if occurrence["kind"] == "annotation":
            annotation = ast
            for token in occurrence["pointer"].split("/")[1:]:
                key = token.replace("~1", "/").replace("~0", "~")
                annotation = annotation[int(key) if isinstance(annotation, list) else key]
            assert annotation["alias"] == occurrence["alias"]
            scopes[annotation["alias"]] = annotation["scope"]
    assert scopes == {"INPUT_FORMAT": "FIELD", "CHECK_INPUT": "STEP"}


@pytest.mark.parametrize("flags", MODES)
def test_invalid_step_scope_in_all_output_modes(tmp_path, flags):
    source = write_spec(tmp_path, "invalid.gasd", f"FLOW check(value: String):\n{INVALID_STEP}\n")
    destination = tmp_path / "ast.json"
    destination.write_bytes(b"existing AST\n")
    result = run_cli(source, *flags)
    assert_annotation_error(result, source, flags, SCOPE_ERROR, 5, INVALID_STEP.index("@"))
    assert destination.read_bytes() == b"existing AST\n"


@pytest.mark.parametrize("flags", MODES[1:4])
def test_invalid_nested_step_arguments(tmp_path, flags):
    nested_step = "        1. VALIDATE value AS TYPE.String @constraint AS CHECK_CONSTRAINT"
    source = write_spec(tmp_path, "nested.gasd", f"FLOW check(value: String):\n    1. IF true:\n{nested_step}\n")
    result = run_cli(source, *flags)
    message = "Annotation @constraint requires argument 'desc'"
    assert_annotation_error(result, source, flags, message, 6, nested_step.index("@"))
    assert not (tmp_path / "ast.json").exists()


@pytest.mark.parametrize("flags", MODES[1:4])
def test_invalid_annotation_in_imported_source(tmp_path, flags):
    entry = write_spec(tmp_path, "entry.gasd", 'IMPORT "./imported.spec"\n', version="1.1")
    imported = write_spec(tmp_path, "imported.spec", f"FLOW check(value: String):\n{INVALID_STEP}\n", version="1.1")
    result = run_cli(entry, *flags)
    assert_annotation_error(result, imported, flags, SCOPE_ERROR, 5, INVALID_STEP.index("@"))
    assert not (tmp_path / "ast.json").exists()


def test_uncaptured_external_import_requires_export_sources(tmp_path):
    source = write_spec(tmp_path, "external.gasd", 'IMPORT "External"\n', version="1.1")
    plain = run_cli(source, "--ast-sem")
    assert plain.returncode == 0, plain.stderr
    export = run_cli(source, "--ast-sem", "--json", "--ast-output", "ast.json")
    assert export.returncode == 1 and export.stdout == "", export.stderr
    report = json.loads(export.stderr)
    assert "CPC-IMPORT" in {error["code"] for item in report["reports"] for error in item["errors"]}
    assert not (tmp_path / "ast.json").exists()


@pytest.mark.parametrize("flags", [(), ("--json",)])
def test_syntax_only_skips_step_annotation_validation(tmp_path, flags):
    source = write_spec(tmp_path, "syntax.gasd", f"FLOW check(value: String):\n{INVALID_STEP}\n")
    result = run_cli(source, "--ast-sem", "--no-validate", *flags)
    assert result.returncode == 0, result.stderr
    assert SCOPE_ERROR not in result.stderr
    if flags:
        ast = json.loads(result.stdout)
        report = json.loads(result.stderr)
        assert ast["kind"] != "SemanticSystem" and "source_inventory" not in ast
        assert report["success"] is True and "semantic_ast_sha512" not in report
    else:
        assert result.stdout == ""
