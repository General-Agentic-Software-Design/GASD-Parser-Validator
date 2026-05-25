import subprocess
import os
import json

def test_standard_json_output_adopts_relative_paths(tmp_path):
    """RT-PARSER-010-01: Standard JSON output without --ast-sem adopts relative paths."""
    test_file = tmp_path / "test.gasd"
    test_file.write_text('CONTEXT: "Regression"\nTARGET: "Python3"\n')
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--json", "test.gasd"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )
    output = result.stdout
    # Expect standard CLI to also sanitize
    assert str(tmp_path) not in output, "Absolute path leaked in standard JSON output"

def test_absolute_path_cli_args_relativized(tmp_path):
    """RT-PARSER-010-02: Absolute paths provided as args are correctly relativized."""
    test_file = tmp_path / "test.gasd"
    test_file.write_text('CONTEXT: "Regression"\nTARGET: "Python3"\n')
    abs_path = str(test_file.resolve())
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--json", "--ast-sem", abs_path],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )
    output = result.stdout
    assert str(tmp_path) not in output, "Absolute CLI argument path leaked into JSON!"

def test_no_validate_ast_output_uses_relative_paths(tmp_path):
    """RT-PARSER-010-03: --no-validate --ast-output uses relative paths in exported AST."""
    test_file = tmp_path / "test.gasd"
    test_file.write_text('VERSION 1.2\nCONTEXT: "Regression"\nTARGET: "Python3"\nTYPE TestType: field: String\n')
    output_file = tmp_path / "output.json"
    abs_path = str(test_file.resolve())
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--no-validate", "--ast-output", str(output_file), abs_path],
        cwd=str(tmp_path),
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Command failed: {result.stderr}"
    assert output_file.exists(), "Output file was not created"
    
    # Read and parse the output JSON
    with open(output_file, 'r') as f:
        ast_data = json.load(f)
    
    # Convert to string to check for any absolute path leaks
    ast_json_str = json.dumps(ast_data)
    
    # Verify no absolute paths leaked into the output
    assert str(tmp_path) not in ast_json_str, "Absolute path leaked in --no-validate --ast-output JSON!"
    
    # Verify sourceFile field uses relative path
    assert "sourceFile" in ast_data, "sourceFile field missing from AST"
    source_file = ast_data["sourceFile"]
    assert not os.path.isabs(source_file), f"sourceFile should be relative, got: {source_file}"
    assert source_file == "test.gasd", f"Expected 'test.gasd', got: {source_file}"
