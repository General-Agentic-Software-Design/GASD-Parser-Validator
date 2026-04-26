"""
Acceptance Tests: Exclusive File Output for --ast-output (US-PARSER-013)
========================================================================
Validates that when --ast-output <output-file> is specified, AST JSON
content is written exclusively to the file and NOT to stdout.
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
        # stdout must not contain any JSON content
        stdout = result.stdout.strip()
        assert "{" not in stdout, f"AST JSON leaked to stdout: {stdout[:200]}"
        assert "SemanticSystem" not in stdout, f"AST node data leaked to stdout: {stdout[:200]}"
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
        assert "asts" in data, "Default stdout behavior broken: no AST JSON on stdout without --ast-output"
    finally:
        os.unlink(fp)


def test_ast_output_content_identity():
    """AT-PARSER-013-04 / AC-PARSER-013-05: File content must be identical to what stdout would produce."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    # Run with --ast-output
    result_file, fp = run_cli("--ast-sem", "--ast-output", out_path)
    try:
        assert result_file.returncode == 0, f"stderr: {result_file.stderr}"
        with open(out_path) as f:
            file_data = json.load(f)

        # Run without --ast-output to get stdout JSON
        result_stdout, fp2 = run_cli("--ast-sem", "--json", file_path=fp)
        stdout_data = json.loads(result_stdout.stdout)

        # The file output is a single SemanticSystem; stdout wraps in {"asts": [...]}
        # Compare the AST content structurally
        assert file_data["kind"] == "SemanticSystem"
        assert stdout_data["asts"][0]["kind"] == "SemanticSystem"
        # Both should have the same types defined
        file_types = {t["name"] for t in file_data.get("types", [])}
        stdout_types = {t["name"] for t in stdout_data["asts"][0].get("types", [])}
        assert file_types == stdout_types, f"Content mismatch: file={file_types}, stdout={stdout_types}"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


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
        # stdout must remain free of AST JSON
        stdout = result.stdout.strip()
        assert "SemanticSystem" not in stdout, f"AST JSON leaked to stdout with --json: {stdout[:200]}"
        assert '"asts":' not in stdout, f"AST JSON leaked to stdout with --json: {stdout[:200]}"
        # File must contain the full output
        assert os.path.exists(out_path), "Output file was not created"
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)
