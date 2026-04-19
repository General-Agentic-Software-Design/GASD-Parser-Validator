import pytest
import subprocess
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli_with_args(*args):
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result

def test_negative_cli_invalid_flag():
    """Negative: Verify standard error exit behavior when invalid flags are provided"""
    result = run_cli_with_args("--invalid-fake-flag-for-testing")
    
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert "unrecognized arguments" in output or "error:" in output, "Did not get standard argparse invalid argument error"
