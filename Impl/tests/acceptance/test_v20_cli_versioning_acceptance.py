import pytest
import subprocess
import os
import json
import tempfile

# The project root — pytest is always invoked from here
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_paths=None):
    """Helper to invoke the CLI and return the result."""
    paths = []
    if file_paths:
        paths = file_paths
    else:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or 'CONTEXT: "Test"\nTARGET: "Py"\n')
        tmp.close()
        paths = [tmp.name]

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", *paths, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    
    # Return paths so they can be cleaned up
    return result, paths

def cleanup(paths):
    for p in paths:
        if os.path.exists(p):
            os.unlink(p)

def test_cli_version_mismatch_11_vs_12():
    """AT-V2-118: --gasd-ver 1.1 Override on VERSION 1.2 file results in LINT-013."""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n'
    result, paths = run_cli("--gasd-ver", "1.1", input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-013" in result.stderr
        assert "Version mismatch" in result.stderr
    finally:
        cleanup(paths)

def test_cli_version_mismatch_12_vs_11():
    """AT-V2-119: --gasd-ver 1.2 Override on VERSION 1.1 file results in LINT-013."""
    content = 'VERSION 1.1\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n'
    result, paths = run_cli("--gasd-ver", "1.2", input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-013" in result.stderr
        assert "Version mismatch" in result.stderr
    finally:
        cleanup(paths)

def test_cli_version_defaulting_to_12():
    """AT-V2-120: No flag on empty version file defaults to 1.2 (strict rules)."""
    # ACHIEVE without POSTCONDITION is LINT-001 error in 1.2
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nFLOW f():\n  1. ACHIEVE "Missing Post"\n'
    result, paths = run_cli(input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-001" in result.stderr
        assert "POSTCONDITION" in result.stderr
    finally:
        cleanup(paths)

def test_cli_version_batch_11():
    """AT-V2-121: --gasd-ver 1.1 processes multiple files with legacy semantics."""
    # ACHIEVE without POSTCONDITION is NOT an error in 1.1 (it might be a warning/info, but not exit code 1)
    content1 = 'VERSION 1.1\nCONTEXT: "C1"\nTARGET: "P"\nFLOW f():\n  1. ACHIEVE "Task1"\n'
    content2 = 'CONTEXT: "C2"\nTARGET: "P"\nFLOW g():\n  1. ACHIEVE "Task2"\n'
    
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write(content1)
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write(content2)
    tmp2.close()
    
    result, paths = run_cli("--gasd-ver", "1.1", file_paths=[tmp1.name, tmp2.name])
    try:
        # Should pass because 1.1 does not elevate LINT-001 to ERROR
        assert result.returncode == 0
    finally:
        cleanup(paths)

def test_gep6_enforcement_lint_001():
    """AT-V2-122: --gasd-ver 1.2 enforces LINT-001 (Missing POSTCONDITION)."""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nFLOW f():\n  1. ACHIEVE "No Post"\n'
    result, paths = run_cli("--gasd-ver", "1.2", input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-001" in result.stderr
    finally:
        cleanup(paths)

def test_gep6_enforcement_lint_002():
    """AT-V2-123: --gasd-ver 1.2 enforces LINT-002 (Missing CONTRACT)."""
    # Create the imported file in a temporary location
    other_path = os.path.join(tempfile.gettempdir(), "other_v2_acceptance.gasd")
    with open(other_path, "w") as f:
        f.write('VERSION 1.2\nNAMESPACE: "Other"\nCONTEXT: "Other"\nTARGET: "Py"\n')
        
    content = f'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nIMPORT "{other_path}"\n'
    result, paths = run_cli("--gasd-ver", "1.2", input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-002" in result.stderr
    finally:
        cleanup(paths)
        if os.path.exists(other_path):
            os.unlink(other_path)

def test_gep6_enforcement_lint_011():
    """AT-V2-124: --gasd-ver 1.2 enforces LINT-011 (Missing AS identifier)."""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\n@retry(3)\nTYPE T: f: String\n'
    result, paths = run_cli("--gasd-ver", "1.2", input_content=content)
    try:
        assert result.returncode == 1
        assert "LINT-011" in result.stderr
    finally:
        cleanup(paths)
