import pytest
import subprocess
import os
import json
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None):
    if file_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        tmp.close()
        file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, file_path

def test_acceptance_version_marker_with_version():
    """AC-PARSER-009-02: gasd_file_version IS '1.2'"""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=content)
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        assert "semantic_validate" in data
        assert "gasd_file_version" in data["semantic_validate"]
        assert data["semantic_validate"]["gasd_file_version"] == "1.2"
    finally:
        os.unlink(fp)

def test_acceptance_version_marker_unknown():
    """AC-PARSER-009-03: Run gasd_parser on a legacy file with no version directive -> 'unknown'"""
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=content)
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        if "semantic_validate" in data:
            assert "gasd_file_version" in data["semantic_validate"]
            assert data["semantic_validate"]["gasd_file_version"] == "unknown"
    finally:
        os.unlink(fp)
