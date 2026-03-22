import pytest
import subprocess
import os

"""
Design Validation: CLI
Mapped from Validation/cli_tests.gasd
"""

def test_design_cli_multiple_files():
    """FLOW test_cli_multiple_files"""
    f1, f2 = "d_cli1.gasd", "d_cli2.gasd"
    with open(f1, "w") as f: f.write('CONTEXT: "C1"\nTARGET: "P"\nTYPE Dummy1: f: String\n')
    with open(f2, "w") as f: f.write('CONTEXT: "C2"\nTARGET: "P"\nTYPE Dummy2: f: String\n')
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", f1, f2], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 0
        assert "Pass:" in result.stderr
        assert "2" in result.stderr
    finally:
        os.remove(f1); os.remove(f2)

def test_design_cli_recursive_traversal():
    """FLOW test_cli_recursive_traversal"""
    os.makedirs("d_cli_dir", exist_ok=True)
    with open("d_cli_dir/f.gasd", "w") as f: f.write('CONTEXT: "C"\nTARGET: "P"\nTYPE Dummy: f: String\n')
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "d_cli_dir/"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 0
        assert "f.gasd" in result.stderr
    finally:
        import shutil
        shutil.rmtree("d_cli_dir")
