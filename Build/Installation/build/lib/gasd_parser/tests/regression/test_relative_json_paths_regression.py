import subprocess
import os

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
