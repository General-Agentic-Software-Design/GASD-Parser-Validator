"""
Acceptance Tests: Exclusive File Output for --ast-output (US-PARSER-013)
========================================================================
Validates that when --ast-output <output-file> is specified, AST JSON
content is written exclusively to the file and NOT to stdout.
Trace: US-PARSER-013
"""

from datetime import datetime
from hashlib import sha512
from itertools import count
import subprocess
import os
import json
import sys
import tempfile
from types import SimpleNamespace
from uuid import UUID

import pytest

from Impl import cli
from Impl.semantic import SemanticNodes

VALID_GASD = 'VERSION 1.2\nCONTEXT: "TestCLI"\nTARGET: "Python3"\nTYPE MyT:\n  f: String\n'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def run_cli(*args, input_content=None, file_path=None):
    """Helper to invoke the CLI and return the result."""
    if file_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or VALID_GASD)
        tmp.close()
        file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, file_path


def test_ast_output_file_contains_valid_json():
    """AT-PARSER-013-01 / AC-PARSER-013-01: --ast-output writes complete AST JSON to the file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--ast-sem", "--ast-output", out_path)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert os.path.exists(out_path), "Output file was not created"
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem", "Output file does not contain a valid SemanticSystem AST"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_ast_output_stdout_suppressed():
    """AT-PARSER-013-02 / AC-PARSER-013-02: stdout must NOT contain AST JSON when --ast-output is specified."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--ast-sem", "--ast-output", out_path)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert result.stdout == ""
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_ast_output_default_stdout_preserved():
    """AT-PARSER-013-03 / AC-PARSER-013-04: Without --ast-output, AST JSON must still go to stdout."""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["kind"] == "SemanticSystem"
        assert json.loads(result.stderr)["success"] is True
    finally:
        os.unlink(fp)


@pytest.mark.parametrize("source", ["file", "stdin"])
def test_ast_output_content_identity(tmp_path, source):
    """AT-PARSER-013-04 / AC-PARSER-013-05: File content must be identical to what stdout would produce."""
    output = tmp_path / "ast.json"
    command = [sys.executable, "-m", "Impl.cli", "--json"]
    options = {"capture_output": True, "check": True, "cwd": PROJECT_ROOT}
    if source == "stdin":
        options["input"] = VALID_GASD.encode("utf-8")
    else:
        spec = tmp_path / "input.gasd"
        spec.write_text(VALID_GASD, encoding="utf-8")
        command.append(str(spec))

    stdout_result = subprocess.run(command, **options)
    file_result = subprocess.run([*command, "--ast-output", str(output)], **options)
    assert file_result.stdout == b""
    stdout_ast = json.loads(stdout_result.stdout)
    file_ast = json.loads(output.read_bytes())
    assert stdout_ast["kind"] == file_ast["kind"] == "SemanticSystem"
    assert stdout_ast["semantic_validate"]["status"] == "PASSED"
    if source == "stdin":
        assert list(stdout_ast["compilationUnit"]["fileNodes"]) == ["stdin"]
    assert comparable_ast(stdout_ast) == comparable_ast(file_ast)


def comparable_ast(document):
    """Omit generated UUIDs, validation time, and the digest that covers them."""
    def strip_node_ids(value):
        if isinstance(value, list):
            for item in value:
                strip_node_ids(item)
        elif isinstance(value, dict):
            if "kind" in value and "sourceMap" in value:
                UUID(value.pop("id"))
            for item in value.values():
                strip_node_ids(item)

    strip_node_ids(document)
    document["semantic_validate"].pop("validation_time")
    document["semantic_validate"].pop("semantic_ast_bytes_sha512")
    return document


def test_ast_output_byte_identity_with_fixed_run_metadata(tmp_path, monkeypatch, capsysbinary):
    """RT-AST-PROVENANCE-015-02: Each destination receives the same provenance."""
    spec = tmp_path / "input.gasd"
    spec.write_text(VALID_GASD, encoding="utf-8")
    output = tmp_path / "ast.json"
    fixed_time = datetime(2026, 1, 1)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "datetime", SimpleNamespace(datetime=SimpleNamespace(utcnow=lambda: fixed_time)))

    def invoke(*args):
        ids = count()
        monkeypatch.setattr(SemanticNodes, "uuid4", lambda: UUID(int=next(ids)))
        monkeypatch.setattr(sys, "argv", ["gasd_parser", str(spec), *args])
        with pytest.raises(SystemExit) as completed:
            cli.main()
        assert completed.value.code == 0
        return capsysbinary.readouterr()

    redirected = invoke("--json")
    exported = invoke("--json", "--ast-output", str(output))

    assert exported.out == b""
    assert redirected.out == output.read_bytes()
    assert json.loads(exported.err)["semantic_validate"] == json.loads(redirected.err)["semantic_validate"]

    file_only = invoke("--ast-output", str(output))
    assert file_only.out == b""
    assert redirected.out == output.read_bytes()

    artifact = json.loads(redirected.out)
    marker = artifact["semantic_validate"]
    assert set(marker) == {
        "status", "parser_version", "build_time", "validation_time", "gasd_file_version",
        "semantic_ast_bytes_sha512", "semantic_ast_content_sha512", "semantic_ast_content_version",
    }
    assert marker["status"] == "PASSED"
    assert marker["gasd_file_version"] == "1.2"
    assert artifact["provenance"]["sources"] == [{
        "path": spec.name,
        "sha512": sha512(spec.read_bytes()).hexdigest(),
    }]


def test_ast_output_unwritable_path():
    """AT-PARSER-013-05 / AC-PARSER-013-06: Unwritable path must cause non-zero exit and stderr error."""
    result, fp = run_cli("--ast-sem", "--ast-output", "/invalid/nonexistent/path/out.json")
    try:
        assert result.returncode != 0, "Parser should exit with non-zero code for unwritable path"
        assert result.stderr.strip() != "", "stderr should contain an error message for unwritable path"
    finally:
        os.unlink(fp)


def test_ast_output_json_flag_no_stdout_leak():
    """AT-PARSER-013-06 / AC-PARSER-013-02: --json --ast-output must not leak JSON to stdout."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--ast-sem", "--json", "--ast-output", out_path)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert result.stdout == ""
        assert json.loads(result.stderr)["success"] is True
        # File must contain the full output
        assert os.path.exists(out_path), "Output file was not created"
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)
