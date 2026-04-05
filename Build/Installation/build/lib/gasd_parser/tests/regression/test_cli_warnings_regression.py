import pytest
import subprocess
import os
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(file_path, *args):
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result

def test_cli_ast_warnings():
    """Verify --ast shows Phase 3 warnings and summary includes them."""
    gasd_content = """CONTEXT: "Test"\nTARGET: "Any"\nNAMESPACE: "n"\nTYPE T:\n  f: UnknownType\n"""
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as tmp:
        tmp.write(gasd_content)
        file_path = tmp.name

    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp.name, "--ast"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode != 0
        
        # Verify tombstone message
        assert "Unknown argument '--ast'" in result.stderr
        assert "Feature removed in GASD 2.0" in result.stderr
    finally:
        os.unlink(tmp.name)

def test_cli_ast_sem_warnings():
    """Validates RT-PARSER-008-02: Warning tracking is passed to --ast-sem"""
    gasd_content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Any"\nNAMESPACE: "n"\nFLOW F:\n  // missing otherwise\n  1. ENSURE "Condition"'
    tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp.write(gasd_content)
    tmp.close()

    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp.name, "--ast-sem"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        print("STDERR: ", result.stderr)
        print("STDOUT: ", result.stdout)
        # Warnings should cause non-zero exit codes if --ast-sem is used (as per recent requirement)
        assert result.returncode != 0
        assert "warning[SEMANTIC MissingOtherwise]" in result.stderr
        assert "error[SEMANTIC MissingOtherwise]" in result.stderr or "warning[SEMANTIC MissingOtherwise]" in result.stderr
    finally:
        os.unlink(tmp.name)
