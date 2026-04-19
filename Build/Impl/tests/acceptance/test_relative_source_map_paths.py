import pytest
import subprocess
import os
import json
import tempfile
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None, cwd=None):
    if file_path is None and input_content is not None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content)
        tmp.close()
        file_path = tmp.name

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
    return result, file_path

def test_at_parser_010_01_current_dir():
    """AT-PARSER-010-01: Run within its directory and verify file is 'test.gasd'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        result, _ = run_cli("--ast-sem", "--json", file_path="test.gasd", cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        # Check sourceMap in at least one node (e.g., the TYPE node)
        type_node = data["asts"][0]["namespaces"]["global"]["types"]["T"]
        assert type_node["sourceMap"]["file"] == "test.gasd"

def test_at_parser_010_02_subdir():
    """AT-PARSER-010-02: Run from parent and verify file is 'subdir/test.gasd'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        file_path = os.path.join(subdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        result, _ = run_cli("--ast-sem", "--json", file_path="subdir/test.gasd", cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        type_node = data["asts"][0]["namespaces"]["global"]["types"]["T"]
        assert type_node["sourceMap"]["file"] == "subdir/test.gasd"

def test_at_parser_010_03_parent_dir():
    """AT-PARSER-010-03: Run from subdir and verify file is '../test.gasd'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        result, _ = run_cli("--ast-sem", "--json", file_path="../test.gasd", cwd=subdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        type_node = data["asts"][0]["namespaces"]["global"]["types"]["T"]
        assert type_node["sourceMap"]["file"] == "../test.gasd"

def test_at_parser_010_04_slash_normalization():
    """AT-PARSER-010-04: Verify forward slashes in output (even if input used backslashes)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        subdir = os.path.join(tmpdir, "sub")
        os.makedirs(subdir)
        file_path = os.path.join(subdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        # Simulate backslash input (if on Unix, this is still a valid single filename, but we want to test relativizer)
        # However, the best way to test this is to provide a path that WOULD have backslashes on Windows.
        # Here we just verify that ANY path in the output uses /
        result, _ = run_cli("--ast-sem", "--json", file_path="sub/test.gasd", cwd=tmpdir)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        
        # Verify no backslashes in any path string
        # We check the compilation unit files and one type node as a sample
        asts = data["asts"][0]
        for f in asts["compilationUnit"]["fileNodes"].keys():
             assert "\\" not in f
             assert "/" in f
        
        type_node = asts["namespaces"]["global"]["types"]["T"]
        assert "\\" not in type_node["sourceMap"]["file"]

def test_ac_parser_010_05_stdin():
    """AC-PARSER-010-05: Verify 'stdin' identifier is preserved."""
    content = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n'
    # Use subprocess.run directly to pipe stdin
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", "-", "--ast-sem", "--json"],
        input=content,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    type_node = data["asts"][0]["namespaces"]["global"]["types"]["T"]
    assert type_node["sourceMap"]["file"] == "stdin"

def test_ac_parser_010_06_structural_neutrality():
    """AC-PARSER-010-06: Verify no absolute paths exist in keys, lists, or any other fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a complex structure
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        file_a = os.path.join(tmpdir, "a.gasd")
        file_b = os.path.join(subdir, "b.gasd")
        
        with open(file_a, "w") as f:
            f.write('VERSION 1.2\nTYPE A: f: String\n')
        with open(file_b, "w") as f:
            f.write('VERSION 1.2\nTYPE B: f: String\n')

        # Run with absolute paths as input to ensure they are relativized in output
        result, _ = run_cli("--ast-sem", "--json", file_a, file_b, cwd=tmpdir)
        assert result.returncode == 0
        raw_output = result.stdout
        
        # 1. Structural Check
        data = json.loads(raw_output)
        comp_unit = data["asts"][0]["compilationUnit"]
        
        # Keys in fileNodes MUST be relative
        for filename in comp_unit["fileNodes"].keys():
            assert not os.path.isabs(filename)
            assert filename in ["a.gasd", "subdir/b.gasd"]
            
        # Items in deterministicOrder MUST be relative
        for filename in comp_unit["deterministicOrder"]:
            assert not os.path.isabs(filename)
            assert filename in ["a.gasd", "subdir/b.gasd"]

        # 2. Comprehensive Leak Check (Audit)
        # We search for the tmpdir path in the raw output string
        # tmpdir on Mac often starts with /var or /private/var
        # We check both the realpath and the original tmpdir string
        assert os.path.realpath(tmpdir) not in raw_output
        assert tmpdir not in raw_output
        
        # Generic check: Absolute paths usually start with / (Unix) or C:\ (Windows)
        # In JSON, paths are escaped, so we check for "/Users" on Mac specifically
        # as a representative for this environment
        if PROJECT_ROOT.startswith("/Users/"):
            assert "/Users/" not in raw_output
