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

def test_regression_cli_version_flag():
    """RT-PARSER-011-01: Execute gasd_parser with -v or --version"""
    result = run_cli_with_args("--version")
    output = result.stdout + result.stderr
    assert "built:" in output or "2." in output or "gasd_parser" in output, "Version string not found for --version flag"

def test_regression_cli_help_flag():
    """RT-PARSER-011-02: Execute gasd_parser with -h or --help"""
    result = run_cli_with_args("--help")
    output = result.stdout + result.stderr
    assert "usage:" in output, "usage not found for --help flag"
