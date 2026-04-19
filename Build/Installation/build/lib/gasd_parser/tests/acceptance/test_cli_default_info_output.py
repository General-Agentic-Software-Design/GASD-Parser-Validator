import pytest
import subprocess
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import pty

def run_cli_empty():
    master, slave = pty.openpty()
    result = subprocess.run(
        ["python3", "-m", "Impl.cli"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT,
        stdin=slave
    )
    os.close(master)
    os.close(slave)
    return result

def test_acceptance_cli_default_output():
    """AT-PARSER-011-01, AT-PARSER-011-02, AT-PARSER-011-03: CLI Default Info Output string check"""
    result = run_cli_empty()
    
    output = result.stdout + result.stderr
    
    assert "Version" in output or "version" in output, "Version string not found in default output"
    assert "Build" in output or "build" in output, "Build info not found in default output"
    assert "usage:" in output, "Standard usage help text not found in default output"
