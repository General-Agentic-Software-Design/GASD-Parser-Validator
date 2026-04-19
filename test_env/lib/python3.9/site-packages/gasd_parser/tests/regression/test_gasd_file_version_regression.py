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

def test_regression_version_marker_legacy():
    """RT-PARSER-009-02: Ensure existing AST consumers do not crash"""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\n'
    result, fp = run_cli("--ast-sem", "--json", input_content=content)
    try:
        assert result.returncode == 0
        try:
            # Emulate an AST consumer extracting the first AST
            data = json.loads(result.stdout)
            # Ensure it has basic structure intact (wrapped in 'asts' due to SemanticASTExporter combining logic)
            ast_payload = data.get("asts", [data])[0] if "asts" in data else data
            assert isinstance(ast_payload, dict)
            # Having gasd_file_version shouldn't break the dict parsing
            marker = data.get("semantic_validate", {})
            if marker:
                assert "gasd_file_version" in marker
        except Exception as e:
            pytest.fail(f"Deserialization crashed: {e}")
    finally:
        os.unlink(fp)
