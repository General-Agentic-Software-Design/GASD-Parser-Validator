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

def test_cli_no_flag_detects_1_2(build_pkg, tmp_path):
    """Verify that the CLI defaults to 1.2 and fails on strict rules without flag."""
    gasd_file = tmp_path / "test.gasd"
    # Create a file missing POSTCONDITION (1.2 strict requirement under LINT-001)
    gasd_file.write_text("CONTEXT: 'test'\nTARGET: 'test'\nNAMESPACE: 'test'\nFLOW DummyFlow:\n  1. ACHIEVE \"something\"\n")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    # We expect this to fail (Exit 1) because of 1.2 strictness violations
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", str(gasd_file)],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 1:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 1
    assert "error[SEMANTIC LINT-001]" in output or "ERROR: " in output

def test_cli_ver_1_1_suppresses_hints(build_pkg, tmp_path):
    """Verify that --gasd-ver 1.1 suppresses 1.2 compatibility hints."""
    gasd_file = tmp_path / "test.gasd"
    gasd_file.write_text("VERSION 1.1\nCONTEXT: 'test'\nTARGET: 'test'\nNAMESPACE: 'test'\nFLOW DummyFlow:\n  1. ACHIEVE \"something\"\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    # We expect this to pass (Exit 0) and be clean
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", str(gasd_file), "--gasd-ver", "1.1"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 0
    assert "error" not in output.lower()
    assert "warning[SEMANTIC LINT-001]" in output

def test_cli_ver_1_2_strict_failure(build_pkg, tmp_path):
    """Verify that --gasd-ver 1.2 enforcement works and shows hints."""
    gasd_file = tmp_path / "test.gasd"
    gasd_file.write_text("VERSION 1.2\nCONTEXT: 'test'\nTARGET: 'test'\nNAMESPACE: 'test'\nFLOW DummyFlow:\n  1. ACHIEVE \"something\"\n")

    env = os.environ.copy()
    env["PYTHONPATH"] = build_pkg
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--ast-sem", str(gasd_file), "--gasd-ver", "1.2"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    if result.returncode != 1:
        print(f"DEBUG OUTPUT:\n{output}")
    assert result.returncode == 1
    assert "error[SEMANTIC LINT-001]" in output or "ERROR: " in output

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

def test_cli_version_mismatch_is_error_in_1_1(build_pkg, tmp_path):
    """Verify that LINT-013 is an ERROR even in 1.1 mode (version mismatch is always an error)."""
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
    assert result.returncode == 1
    assert "LINT-013" in output
    assert "version mismatch" in output.lower()

