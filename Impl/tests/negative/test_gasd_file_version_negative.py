import json
import os
import subprocess
import tempfile

import pytest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

VALID_GASD_12 = """VERSION 1.2
CONTEXT: "Negative"
TARGET: "Python3"
TYPE T:
    f: String
"""

MALFORMED_NO_VERSION = """CONTEXT: "Broken"
TARGET: "Python3"
TYPE T:
    f: String
TYPE T:
    g: String
"""


def run_cli(*args, input_content=None, file_path=None):
    if file_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or VALID_GASD_12)
        tmp.close()
        file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT,
    )
    return result, file_path


def assert_dual_version_projection(data, expected_version):
    assert data["semantic_validate"]["gasd_file_version"] == expected_version
    assert data["metadata"]["version"] == expected_version
    assert data["metadata"]["version"] == data["semantic_validate"]["gasd_file_version"]


def parse_optional_json(stdout):
    if not stdout.strip():
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return None


def test_negative_version_marker_malformed():
    """AT-PARSER-009-03: malformed input without VERSION reports unknown when JSON is emitted."""
    result, fp = run_cli("--ast-sem", "--json", input_content=MALFORMED_NO_VERSION)
    try:
        assert result.returncode != 0

        data = parse_optional_json(result.stdout)
        if data is not None and "semantic_validate" in data:
            assert data["semantic_validate"]["gasd_file_version"] == "unknown"
    finally:
        os.unlink(fp)


def test_negative_metadata_version_malformed():
    """AC-PARSER-009-05 / AC-PARSER-009-06: malformed JSON output cannot diverge if emitted."""
    result, fp = run_cli("--ast-sem", "--json", input_content=MALFORMED_NO_VERSION)
    try:
        assert result.returncode != 0

        data = parse_optional_json(result.stdout)
        if data is not None and "metadata" in data and "semantic_validate" in data:
            assert_dual_version_projection(data, "unknown")
    finally:
        os.unlink(fp)


def test_negative_version_projection_mismatch():
    """AC-PARSER-009-06: divergent semantic_validate and metadata versions are contract failures."""
    mismatched_payload = {
        "metadata": {"version": "1.1"},
        "semantic_validate": {"gasd_file_version": "1.2"},
    }

    with pytest.raises(AssertionError):
        assert_dual_version_projection(mismatched_payload, "1.2")


def test_negative_root_level_gasd_file_version():
    """AC-PARSER-009-01 / AC-PARSER-009-05: version is not emitted as a stray root field."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_12)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        assert "gasd_file_version" not in data
        assert "gasd_file_version" not in data["metadata"]
        assert "version" in data["metadata"]
        assert_dual_version_projection(data, "1.2")
    finally:
        os.unlink(fp)
