import pytest
import subprocess
import os
import json
import tempfile

VALID_GASD = 'CONTEXT: "TestCLI"\nTARGET: "Python3"\nTYPE MyT:\n  f: String\n'
INVALID_GASD = "NOT VALID GASD SYNTAX AT ALL ::::: {{{{"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None):
    if file_path is None:
        with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as tmp:
            tmp.write(input_content or VALID_GASD)
            file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, file_path

def test_cli_human_readable_success():
    """Verify success output format: OK Passed + Summary"""
    result, fp = run_cli()
    try:
        assert result.returncode == 0
        assert f"OK Passed: {fp}" in result.stderr
        assert "--- Summary ---" in result.stderr
        assert "Files Validated: 1" in result.stderr
        assert "Pass:            1" in result.stderr
        assert "Failed:          0" in result.stderr
    finally:
        os.unlink(fp)

def test_cli_human_readable_failure():
    """Verify failure output format: ERROR + Summary"""
    result, fp = run_cli(input_content=INVALID_GASD)
    try:
        assert result.returncode == 1
        assert f"ERROR: {fp} failed validation" in result.stderr
        assert "--- Summary ---" in result.stderr
        assert "Files Validated: 1" in result.stderr
        assert "Pass:            0" in result.stderr
        assert "Failed:          1" in result.stderr
    finally:
        os.unlink(fp)

def test_cli_json_ast():
    """Verify --json --ast combines AST into the response"""
    result, fp = run_cli("--ast", "--json")
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "asts" in data
        assert isinstance(data["asts"], list)
        assert data["asts"][0]["kind"] == "GASDFile"
    finally:
        os.unlink(fp)

def test_cli_json_sem_ast():
    """Verify --json --ast-sem combines Semantic AST into the response"""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "asts" in data
        assert isinstance(data["asts"], list)
        assert data["asts"][0]["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)

def test_cli_no_ast_printed_without_json():
    """Verify --ast alone does not print raw JSON to stdout"""
    result, fp = run_cli("--ast")
    try:
        assert result.returncode == 0
        assert f"OK Passed: {fp}" in result.stderr
        # With --ast, JSON is NOT printed to stdout unless --json is specified
        assert not result.stdout.strip().startswith("{")
        assert '"kind": "GASDFile"' not in result.stdout
    finally:
        os.unlink(fp)

def test_semast_cli_activation():
    """Updated to use --json because raw JSON output is now suppressed without it"""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["asts"][0]["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)

def test_semast_cli_output_dir():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name
    result, fp = run_cli("--ast-sem", "--ast-output", out_path)
    try:
        assert result.returncode == 0
        assert os.path.exists(out_path)
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)

def test_semast_cli_combine():
    """Updated to use --json to get structured combined output"""
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write('CONTEXT: "C1"\nTARGET: "P"\nTYPE T1:\n  f: String\n')
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write('CONTEXT: "C2"\nTARGET: "P"\nTYPE T2:\n  g: Integer\n')
    tmp2.close()
    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast", "--ast-combine", "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # In combined mode with --json, we get a list of asts in the "asts" key (or similar)
        # Actually our implementation of ast_combine might be different. Let's check cli.py logic.
        assert "asts" in data
        assert len(data["asts"]) == 2
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)

def test_semast_cli_errors():
    result, fp = run_cli("--json", input_content=INVALID_GASD)
    try:
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["success"] is False
        assert data["failureCount"] == 1
    finally:
        os.unlink(fp)

def test_semast_cli_regression_missing_file():
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", "nonexistent_file_12345.gasd", "--ast-sem"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    assert result.returncode == 1
    assert "Error: Path not found" in result.stderr

# ===================================================================
# Cross-File Regression Tests
# ===================================================================

def test_semast_cli_regression_multi_file():
    # RT-X-SEMAST-011-01
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as f1:
        f1.write('CONTEXT: "A"\nTARGET: "P"\nTYPE T1: f: String\n')
        fp1 = f1.name
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as f2:
        f2.write('CONTEXT: "A"\nTARGET: "P"\nTYPE T2: g: Integer\n')
        fp2 = f2.name
        
    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", fp1, fp2, "--ast-sem", "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # Should have a single SemanticSystem if --ast-combine (default or implied)
        assert data["asts"][0]["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp1)
        os.unlink(fp2)

def test_semast_cli_regression_deterministic_errors():
    # RT-X-SEMAST-011-02
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as f1:
        f1.write('CONTEXT: "A"\nTARGET: "P"\nINVALID')
        fp1 = f1.name
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as f2:
        f2.write('CONTEXT: "A"\nTARGET: "P"\nINVALID')
        fp2 = f2.name
        
    try:
        r1 = subprocess.run(["python3", "-m", "Impl.cli", fp1, fp2], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": PROJECT_ROOT}, cwd=PROJECT_ROOT)
        r2 = subprocess.run(["python3", "-m", "Impl.cli", fp2, fp1], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": PROJECT_ROOT}, cwd=PROJECT_ROOT)
        # Errors should be in the same order regardless of input order (if sorted by file path)
        assert r1.stderr == r2.stderr
    finally:
        os.unlink(fp1)
        os.unlink(fp2)
