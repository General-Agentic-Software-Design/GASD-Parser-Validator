import json
import os
import subprocess
import tempfile


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

VALID_GASD_12 = """VERSION 1.2
CONTEXT: "Regression"
TARGET: "Python3"
TYPE T:
    f: String
"""

VALID_GASD_NO_VERSION = """CONTEXT: "LegacyRegression"
TARGET: "Python3"
TYPE T:
    f: String
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


def legacy_consumer_read(payload):
    """Emulate a tolerant JSON consumer that ignores unknown metadata fields."""
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)
    ast_payload = decoded.get("asts", [decoded])[0] if "asts" in decoded else decoded

    return {
        "kind": ast_payload.get("kind"),
        "types": ast_payload.get("types", []),
        "nodes": ast_payload.get("nodes", []),
    }


def assert_versions_match(data, expected_version):
    assert data["semantic_validate"]["gasd_file_version"] == expected_version
    assert data["metadata"]["version"] == expected_version
    assert data["metadata"]["version"] == data["semantic_validate"]["gasd_file_version"]


def test_regression_version_marker_legacy():
    """RT-PARSER-009-02: existing consumers tolerate semantic_validate.gasd_file_version."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_12)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        view = legacy_consumer_read(data)
        assert isinstance(view, dict)
        assert "gasd_file_version" in data["semantic_validate"]
    finally:
        os.unlink(fp)


def test_regression_metadata_version_legacy():
    """RT-PARSER-009-03: existing consumers tolerate metadata.version."""
    payload = {
        "metadata": {"context": "Regression", "target": "Python3", "version": "1.2"},
        "semantic_validate": {"status": "PASSED", "gasd_file_version": "1.2"},
        "kind": "SemanticSystem",
        "types": [{"name": "T"}],
        "nodes": [],
    }

    view = legacy_consumer_read(payload)

    assert view["kind"] == "SemanticSystem"
    assert view["types"] == [{"name": "T"}]
    assert payload["metadata"]["version"] == payload["semantic_validate"]["gasd_file_version"]


def test_regression_legacy_files_without_version():
    """RT-PARSER-009-01: legacy files without VERSION do not crash and project unknown."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_NO_VERSION)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        assert_versions_match(data, "unknown")
        assert isinstance(legacy_consumer_read(data), dict)
    finally:
        os.unlink(fp)
