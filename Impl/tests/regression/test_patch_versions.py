"""BUG-5 coverage for VERSION declarations, inherited lint rules, and CLI reports."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _source(header, field_type="String"):
    return (
        f'{header}\nCONTEXT: "Version header"\nTARGET: "Python3"\n'
        f"TYPE Example: value: {field_type}\n"
    )


def _cli(*args, source=None):
    return subprocess.run(
        [sys.executable, "-m", "Impl.cli", *args],
        cwd=PROJECT_ROOT,
        input=source,
        capture_output=True,
        text=True,
        timeout=15,
    )


@pytest.mark.parametrize("version", ["1.2", "1.2.0", "1.2.1"])
def test_semantic_ast_preserves_declared_version(version):
    result = _cli("--json", "-", source=_source(f"VERSION {version}"))

    assert result.returncode == 0, result.stderr
    ast = json.loads(result.stdout)
    assert ast["metadata"]["version"] == version
    assert ast["semantic_validate"]["gasd_file_version"] == version


def test_file_export_preserves_patch_version_with_explicit_selector(tmp_path):
    source = tmp_path / "version.gasd"
    source.write_text(_source("VERSION 1.2.1"), encoding="utf-8")
    output = tmp_path / "ast.json"
    result = _cli("--gasd-ver", "1.2", "--ast-output", str(output), str(source))

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == ""
    ast = json.loads(output.read_text(encoding="utf-8"))
    assert ast["metadata"]["version"] == "1.2.1"
    assert ast["semantic_validate"]["gasd_file_version"] == "1.2.1"


def test_syntax_ast_preserves_patch_version():
    result = _cli("--json", "--no-validate", "-", source=_source("VERSION 1.2.1"))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["version"] == "1.2.1"


def test_quoted_version_with_colon_remains_valid():
    result = _cli("--json", "-", source=_source('VERSION: "1.2.1"'))

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["metadata"]["version"] == "1.2.1"


@pytest.mark.parametrize(
    ("version", "exit_code", "severity"),
    [
        ("1.1", 0, "INFO"),
        ("1.2", 1, "ERROR"),
        ("1.2.0", 1, "ERROR"),
        ("1.2.1", 1, "ERROR"),
        ('"1.2.1"', 1, "ERROR"),
    ],
)
def test_patch_version_inherits_field_annotation_lint(version, exit_code, severity):
    result = _cli(
        "--json", "-", source=_source(f"VERSION {version}", "String @min_length(1)")
    )

    assert result.returncode == exit_code, result.stderr
    errors = json.loads(result.stderr)["reports"][0]["errors"]
    assert [error["severity"] for error in errors if error.get("code") == "LINT-011"] == [severity]


def test_incompatible_selector_reports_one_error_with_declared_version():
    result = _cli("--json", "--gasd-ver", "1.1", "-", source=_source("VERSION 1.2.1"))

    assert result.returncode == 1, result.stderr
    errors = json.loads(result.stderr)["reports"][0]["errors"]
    assert [(error.get("code"), error["severity"]) for error in errors] == [("LINT-013", "ERROR")]
    assert "1.2.1" in errors[0]["message"]


@pytest.mark.parametrize("header", ["VERSION 1.2.", "VERSION 1.2.1.0", "VERSION 1.2.-1"])
@pytest.mark.parametrize("args", [(), ("--no-validate",)])
def test_malformed_header_prints_one_failure_banner_and_diagnostic(header, args):
    result = _cli(*args, "-", source=_source(header))

    assert result.returncode == 1, result.stdout + result.stderr
    console = result.stdout + result.stderr
    assert console.count("ERROR: stdin failed validation") == 1
    assert console.count("error[SYNTAX]") == 1


@pytest.mark.parametrize("header", ["VERSION 1.2.", "VERSION 1.2.1.0", "VERSION 1.2.-1"])
def test_malformed_header_has_one_json_error_and_no_ast(header):
    result = _cli("--json", "-", source=_source(header))

    assert result.returncode == 1, result.stderr
    assert result.stdout == ""
    report = json.loads(result.stderr)
    assert report["failureCount"] == 1
    assert report["reports"][0]["errorCount"] == 1
    assert [error["type"] for error in report["reports"][0]["errors"]] == ["SYNTAX"]
