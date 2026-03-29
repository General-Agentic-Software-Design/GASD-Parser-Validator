import pytest
import subprocess
import os

"""
Acceptance Test for US-PARSER-006: Bulk Implementation Search
@trace #AT-PARSER-006-01, #AT-PARSER-006-02, #AC-PARSER-006-03
"""

def test_cli_multiple_files():
    """AT-PARSER-006-01: Multiple specific files can be passed."""
    # Create temp files with unique symbols to avoid DuplicateSymbol errors in aggregate system
    with open("temp1.gasd", "w") as f: f.write('CONTEXT: "T1"\nTARGET: "P"\nTYPE Dummy1: f: String\n')
    with open("temp2.gasd", "w") as f: f.write('CONTEXT: "T2"\nTARGET: "P"\nTYPE Dummy2: f: String\n')
    
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "temp1.gasd", "temp2.gasd"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 0
        # Status messages moved to stderr
        assert "temp1.gasd" in result.stderr
        assert "temp2.gasd" in result.stderr
        assert "Pass:" in result.stderr
        assert "2" in result.stderr
    finally:
        os.remove("temp1.gasd")
        os.remove("temp2.gasd")

def test_cli_recursive_traversal():
    """AT-PARSER-006-02: Recursive folder traversal search."""
    # Using existing Specs/ folder if it exists, or creating a small structure
    os.makedirs("test_dir/sub", exist_ok=True)
    with open("test_dir/f1.gasd", "w") as f: f.write('CONTEXT: "D1"\nTARGET: "P"\nTYPE Dummy1: f: String\n')
    with open("test_dir/sub/f2.gasd", "w") as f: f.write('CONTEXT: "D2"\nTARGET: "P"\nTYPE Dummy2: f: String\n')
    
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "test_dir/"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 0
        # Status messages moved to stderr
        assert "f1.gasd" in result.stderr
        assert "f2.gasd" in result.stderr
        assert "Pass:" in result.stderr
        assert "2" in result.stderr
    finally:
        import shutil
        shutil.rmtree("test_dir")

def test_cli_exit_code_on_failure():
    """AC-PARSER-006-03: Exit code 1 if any file fails."""
    with open("fail.gasd", "w") as f: f.write("INVALID SYNTAX")
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "fail.gasd"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 1
    finally:
        os.remove("fail.gasd")
