import subprocess
import os
import pytest

def test_cli_strict_warnings():
    """
    Regression Test: Ensure that a semantic warning causes a non-zero exit code
    even in standard validation mode (without --ast-sem).
    """
    gasd_content = """
CONTEXT: "Strict Warning Test"
TARGET: "JavaScript"
NAMESPACE: "test"

TYPE Sample:
    id: Integer

FLOW main:
    1. ENSURE "No Otherwise path"
    2. LOG "Done"
"""
    # This should trigger MissingOtherwise warning
    with open("test_strict.gasd", "w") as f:
        f.write(gasd_content)
    
    try:
        # Run standard validation
        result = subprocess.run(
            ["python3", "-m", "gasd_parser", "test_strict.gasd"],
            capture_output=True,
            text=True
        )
        
        # Should fail (exit code 1) due to strict warnings
        assert result.returncode != 0
        assert "warning[SEMANTIC MissingOtherwise]" in result.stderr
        assert "failed validation" in result.stderr
    finally:
        if os.path.exists("test_strict.gasd"):
            os.remove("test_strict.gasd")

def test_multi_doc_alias_resolution():
    """
    Regression Test: Ensure that aliased cross-file type references resolve correctly.
    """
    shared_content = """
CONTEXT: "Shared"
TARGET: "TypeScript"
NAMESPACE: "com.shared"
TYPE User:
    name: String
"""
    service_content = """
CONTEXT: "Service"
TARGET: "TypeScript"
IMPORT "shared.gasd" AS Common
TYPE Request:
    user: Common.User
"""
    
    os.makedirs("test_multi", exist_ok=True)
    with open("test_multi/shared.gasd", "w") as f:
        f.write(shared_content)
    with open("test_multi/service.gasd", "w") as f:
        f.write(service_content)
        
    try:
        # Run validation on directory
        result = subprocess.run(
            ["python3", "-m", "gasd_parser", "test_multi/"],
            capture_output=True,
            text=True
        )
        
        # Should pass with 0 warnings/errors
        assert result.returncode == 0
        assert "Warnings:        0" in result.stdout or "Warnings:        0" in result.stderr
        assert "OK Passed: " in result.stdout or "OK Passed: " in result.stderr
    finally:
        import shutil
        if os.path.exists("test_multi"):
            shutil.rmtree("test_multi")
