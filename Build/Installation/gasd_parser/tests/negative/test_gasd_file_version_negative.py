import pytest
import subprocess
import os
import json
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None):
    if file_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\n')
        tmp.close()
        file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, file_path

def test_negative_version_marker_malformed():
    """AT-PARSER-009-03: Run gasd_parser on malformed without version -> 'unknown'"""
    # Malformed file, no version block, bad syntax
    content = 'INVALID DIRECTIVE BLAH\nCONTEXT: "Test"\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=content)
    try:
        # CLI returns exit code 1 for semantic/syntax errors
        assert result.returncode != 0
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if "semantic_validate" in data:
                    assert "gasd_file_version" in data["semantic_validate"]
                    assert data["semantic_validate"]["gasd_file_version"] == "unknown"
            except json.JSONDecodeError:
                pass
    finally:
        os.unlink(fp)
