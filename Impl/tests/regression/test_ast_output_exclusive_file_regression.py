"""
Regression Tests: Exclusive File Output for --ast-output (US-PARSER-013)
========================================================================
Ensures that existing --ast-output and --ast-sem workflows continue to
function correctly after the exclusive file output change.
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


def test_regression_ast_combine_with_ast_output():
    """RT-PARSER-013-01: --ast-combine with --ast-output must write aggregated AST exclusively to file."""
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write('CONTEXT: "C1"\nTARGET: "P"\nTYPE T1:\n  f: String\n')
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write('CONTEXT: "C2"\nTARGET: "P"\nTYPE T2:\n  g: Integer\n')
    tmp2.close()

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    try:
        command = ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast-combine", "--json"]
        options = {"capture_output": True, "text": True, "cwd": PROJECT_ROOT}
        result = subprocess.run([*command, "--ast-output", out_path], **options)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert result.stdout == ""
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem"
        assert len(data["compilationUnit"]["fileNodes"]) == 2

        redirected = subprocess.run(command, check=True, **options)
        stdout_data = json.loads(redirected.stdout)
        assert stdout_data["kind"] == "SemanticSystem"
        assert stdout_data["compilationUnit"]["fileNodes"].keys() == data["compilationUnit"]["fileNodes"].keys()
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_regression_no_validate_with_ast_output():
    """RT-PARSER-013-02: --no-validate with --ast-output must write AST exclusively to file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--json", "--no-validate", "--ast-output", out_path, input_content=VALID_GASD.replace("TestCLI", "Café"))
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert result.stdout == ""
        redirected = subprocess.run(
            ["python3", "-m", "Impl.cli", "--json", "--no-validate", fp],
            capture_output=True, check=True, cwd=PROJECT_ROOT,
        )
        with open(out_path, "rb") as f:
            assert redirected.stdout == f.read()
        assert json.loads(redirected.stdout)["kind"] == "GASDFile"
        assert "Café".encode("utf-8") in redirected.stdout
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_regression_default_stdout_unchanged():
    """RT-PARSER-013-03: Without --ast-output, --ast-sem --json must still emit JSON to stdout."""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)
