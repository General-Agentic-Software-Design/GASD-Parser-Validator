import json
import os
import subprocess
import tempfile


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

VALID_GASD_12 = """VERSION 1.2
CONTEXT: "Test"
TARGET: "Python3"
TYPE T:
    f: String
"""

VALID_GASD_NO_VERSION = """CONTEXT: "Legacy"
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


def assert_dual_version_projection(data, expected_version):
    assert "semantic_validate" in data, "Semantic AST JSON must include semantic_validate"
    assert "metadata" in data, "Semantic AST JSON must include root metadata"

    marker = data["semantic_validate"]
    metadata = data["metadata"]

    assert marker["gasd_file_version"] == expected_version
    assert metadata["version"] == expected_version
    assert metadata["version"] == marker["gasd_file_version"]


def test_acceptance_version_marker_with_version():
    """AT-PARSER-009-01 / AT-PARSER-009-04: explicit VERSION 1.2 is projected in both places."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_12)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        assert_dual_version_projection(data, "1.2")
    finally:
        os.unlink(fp)


def test_acceptance_version_marker_unknown():
    """AT-PARSER-009-02 / AT-PARSER-009-04: missing VERSION projects unknown in both places."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_NO_VERSION)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        assert_dual_version_projection(data, "unknown")
    finally:
        os.unlink(fp)


def test_acceptance_metadata_version_stdout():
    """AT-PARSER-009-04: --ast-sem --json includes metadata.version equal to marker version."""
    result, fp = run_cli("--ast-sem", "--json", input_content=VALID_GASD_12)
    try:
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)

        assert "version" in data["metadata"]
        assert data["metadata"]["version"] == data["semantic_validate"]["gasd_file_version"]
    finally:
        os.unlink(fp)


def test_acceptance_metadata_version_ast_output():
    """AT-PARSER-009-05: --ast-sem --ast-output writes metadata.version to the output file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name

    result, fp = run_cli("--ast-sem", "--ast-output", out_path, input_content=VALID_GASD_12)
    try:
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out_path), "AST output file was not created"

        with open(out_path) as f:
            data = json.load(f)

        assert_dual_version_projection(data, "1.2")
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)
