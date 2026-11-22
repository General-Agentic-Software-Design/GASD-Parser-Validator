"""
Negative Tests: Exclusive File Output for --ast-output (US-PARSER-013)
======================================================================
Validates error handling and edge cases for --ast-output exclusive file behavior.
Trace: US-PARSER-013
"""

import pytest
import subprocess
import os
import json
import tempfile

VALID_GASD = 'CONTEXT: "TestCLI"\nTARGET: "Python3"\nTYPE MyT:\n  f: String\n'

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


def test_negative_permission_denied_path():
    """AC-PARSER-013-06: Permission-denied path must cause non-zero exit and stderr error."""
    result, fp = run_cli("--ast-sem", "--ast-output", "/root/forbidden.json")
    try:
        assert result.returncode != 0, "Parser should exit with non-zero code for permission-denied path"
        assert result.stderr.strip() != "", "stderr should contain an error for permission-denied path"
    finally:
        os.unlink(fp)


def test_negative_directory_as_output_path():
    """AC-PARSER-013-06: A directory path instead of a file path must be handled gracefully."""
    result, fp = run_cli("--ast-sem", "--ast-output", "/tmp/")
    try:
        assert result.returncode != 0, "Parser should exit with non-zero code when output path is a directory"
        assert result.stderr.strip() != "", "stderr should contain an error when output path is a directory"
    finally:
        os.unlink(fp)


def test_negative_nonexistent_parent_directory():
    """AC-PARSER-013-06: Output path with nonexistent parent directory must fail."""
    result, fp = run_cli("--ast-sem", "--ast-output", "/nonexistent/deeply/nested/out.json")
    try:
        assert result.returncode != 0, "Parser should exit with non-zero code for nonexistent parent directory"
        assert result.stderr.strip() != "", "stderr should contain an error for nonexistent parent path"
    finally:
        os.unlink(fp)


def test_negative_no_json_leak_under_combined_flags():
    """AC-PARSER-013-02: No JSON must leak to stdout under any flag combination with --ast-output."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--ast-sem", "--json", "--ast-output", out_path)
    try:
        assert result.returncode == 0
        assert result.stdout == ""
        assert json.loads(result.stderr)["success"] is True
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_negative_empty_output_path():
    result, fp = run_cli("--json", "--ast-output", "")
    try:
        assert result.returncode == 1
        assert result.stdout == ""
        error = json.loads(result.stderr)["outputError"]
        assert error["path"] is None
        assert "Could not write AST" in error["message"]
    finally:
        os.unlink(fp)


@pytest.mark.parametrize("file_destination", [False, True])
def test_negative_no_ast_available(tmp_path, file_destination):
    output = tmp_path / "ast.json"
    output.write_text("previous contents", encoding="utf-8")
    flags = ["--ast-output", str(output)] if file_destination else []
    result, fp = run_cli("--json", *flags, input_content="TYPE ???")
    try:
        assert result.returncode == 1
        assert result.stdout == ""
        assert output.read_text(encoding="utf-8") == "previous contents"
        report = json.loads(result.stderr)
        assert report["failureCount"] == 1
        errors = report["reports"][0]["errors"]
        assert any("token recognition error" in error["message"] for error in errors)
    finally:
        os.unlink(fp)
