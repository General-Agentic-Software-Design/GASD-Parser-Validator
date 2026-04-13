import pytest
import subprocess
import os
import json
import tempfile
import re

# The project root — pytest is always invoked from here
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None):
    """Helper to invoke the CLI and return the result."""
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

def is_iso8601(timestamp):
    # Basic ISO-8601 regex check: YYYY-MM-DDTHH:MM:SSZ or with offset
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'
    return re.match(pattern, timestamp) is not None

def test_marker_presence_and_success():
    """AT-PARSER-008-01, AC-PARSER-008-01, AC-PARSER-008-02
    ENSURE 'semantic_validate' marker is present at root levels and indicates PASSED for valid files.
    """
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        # Verify marker presence
        assert "semantic_validate" in data
        marker = data["semantic_validate"]
        
        # Verify status
        assert marker["status"] == "PASSED"
    finally:
        os.unlink(fp)

def test_marker_metadata_fields():
    """AT-PARSER-008-02, AT-PARSER-008-03, AC-PARSER-008-03, AC-PARSER-008-04, AC-PARSER-008-05
    ENSURE marker contains parser_version, build_time, and validation_time.
    """
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        marker = data["semantic_validate"]
        
        # Verify version
        assert "parser_version" in marker
        assert isinstance(marker["parser_version"], str)
        assert len(marker["parser_version"]) > 0
        
        # Verify timestamps
        assert "build_time" in marker
        assert is_iso8601(marker["build_time"])
        
        assert "validation_time" in marker
        assert is_iso8601(marker["validation_time"])
    finally:
        os.unlink(fp)

def test_marker_failure_integrity():
    """AT-PARSER-008-04, AC-PARSER-008-06
    ENSURE marker indicates FAILED (or is absent) when semantic validation fails.
    """
    # File with semantic error (Duplicate Symbol)
    invalid_content = 'VERSION 1.2\nCONTEXT: "Err"\nTARGET: "Py"\nTYPE T: f: String\nTYPE T: g: Integer\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=invalid_content)
    try:
        # CLI returns exit code 1 for semantic errors
        assert result.returncode == 1
        
        # Even on failure, if it produces JSON, the marker must reflect failure
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if "semantic_validate" in data:
                    assert data["semantic_validate"]["status"] == "FAILED"
            except json.JSONDecodeError:
                pass # If it's not JSON on failure, that's also acceptable under some modes
    finally:
        os.unlink(fp)

def test_marker_version_11_exclusion():
    """RT-PARSER-008-01: ENSURE marker is NOT present for VERSION 1.1 files.
    """
    content_v11 = 'VERSION 1.1\nCONTEXT: "Legacy"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=content_v11)
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Validation marker is a v1.2+ feature
        assert "semantic_validate" not in data
    finally:
        os.unlink(fp)

def test_marker_no_json_exclusion():
    """AC-PARSER-008-01: ENSURE marker is NOT present when --json is not used.
    """
    result, fp = run_cli("--ast-sem")
    try:
        assert result.returncode == 0
        # When --json is not present, output is usually stdout/stderr text
        # But we check that no JSON blob containing the marker is leaked to stdout
        assert "semantic_validate" not in result.stdout
    finally:
        os.unlink(fp)
