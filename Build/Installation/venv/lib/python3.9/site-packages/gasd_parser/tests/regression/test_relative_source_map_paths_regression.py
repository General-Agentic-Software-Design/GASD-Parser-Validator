import pytest
import subprocess
import os
import json
import tempfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None, cwd=None):
    cli_args = ["python3", "-m", "Impl.cli"]
    if file_path:
        cli_args.append(file_path)
    cli_args.extend(args)

    result = subprocess.run(
        cli_args,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=cwd or PROJECT_ROOT
    )
    return result

def test_rt_parser_010_01_json_consistency():
    """RT-PARSER-010-01: Ensure standard JSON output also uses relative paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        # Run WITHOUT --ast-sem, just --json
        result = run_cli("--json", file_path="test.gasd", cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        # Standard JSON output has 'reports' list containing report objects
        report = data["reports"][0]
        assert report["sourceFile"] == "test.gasd"

def test_rt_parser_010_02_absolute_cli_relativization():
    """RT-PARSER-010-02: Absolute paths in CLI are relativized in output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        # Pass ABSOLUTE path to CLI but run from the same directory
        result = run_cli("--ast-sem", "--json", file_path=os.path.abspath(file_path), cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        type_node = data["asts"][0]["namespaces"]["global"]["types"]["T"]
        assert type_node["sourceMap"]["file"] == "test.gasd"

def test_rt_parser_010_03_structural_consistency():
    """RT-PARSER-010-03: Ensure absolute CLI inputs don't leak into the structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nTYPE T: f: String\n')
        
        # Pass absolute path
        abs_path = os.path.abspath(file_path)
        result = run_cli("--ast-sem", "--json", file_path=abs_path, cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        # Check that the absolute path is NOT used as a key in fileNodes
        file_nodes = data["asts"][0]["compilationUnit"]["fileNodes"]
        assert abs_path not in file_nodes
        assert "test.gasd" in file_nodes
