import pytest
import subprocess
import os
import shutil
from pathlib import Path

@pytest.fixture
def build_pkg():
    """Ensure the package is built before running tests."""
    # This might be slow if run every time, but necessary for CLI tests
    subprocess.run(["bash", "Build/Installation/package.sh"], check=True, capture_output=True)
    return os.path.abspath("Build/Installation")

def test_cli_no_flag_detects_1_2(build_pkg):
    """Verify that the CLI detects 1.2 and fails on strict rules without flag."""
    # Use a directory that definitely has 1.2 files (Design)
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    # We expect this to fail (Exit 1) because Design/ has strictness violations in 1.2
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", "Design"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 1:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 1
    assert "info[SEMANTIC LINT-001]" in output or "warning[SEMANTIC LINT-001]" in output
    assert "GASD 1.2 compatibility" in output

def test_cli_ver_1_1_suppresses_hints(build_pkg):
    """Verify that --gasd-ver 1.1 suppresses 1.2 compatibility hints."""
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    # We expect this to pass (Exit 0) and be clean
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", "Design", "--gasd-ver", "1.1"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 0
    assert "GASD 1.2 compatibility" not in output
    import re
    assert re.search(r"Warnings:\s+0", output)

def test_cli_ver_1_2_strict_failure(build_pkg):
    """Verify that --gasd-ver 1.2 enforcement works and shows hints."""
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", "Design", "--gasd-ver", "1.2"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 1:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 1
    assert "info[SEMANTIC LINT-001]" in output
    assert "GASD 1.2 compatibility" in output

def test_cli_version_mismatch_is_error_in_1_2(build_pkg, tmp_path):
    """Verify that LINT-013 is an ERROR in 1.2 mode."""
    # Create a 1.1 file but enforce 1.2
    gasd_file = tmp_path / "legacy.gasd"
    gasd_file.write_text("VERSION 1.1\nCONTEXT: 'test'\nTARGET: 'test'\nNAMESPACE: 'test'\nTYPE Dummy: string\n")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", str(gasd_file), "--gasd-ver", "1.2"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    print(f"DEBUG LINT-013 OUTPUT:\n{output}")
    assert result.returncode == 1
    assert "LINT-013" in output
    assert "error" in output.lower()
    assert "version mismatch" in output.lower()

def test_cli_version_mismatch_is_hidden_in_1_1(build_pkg, tmp_path):
    """Verify that LINT-013 is hidden (INFO) in 1.1 mode."""
    # Create a 1.2 file but enforce 1.1
    gasd_file = tmp_path / "modern.gasd"
    gasd_file.write_text("VERSION 1.2\nNAMESPACE: 'test'\n")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", str(gasd_file), "--gasd-ver", "1.1"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    assert result.returncode == 0
    assert "LINT-013" not in output
