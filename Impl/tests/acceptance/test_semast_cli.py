import pytest
import subprocess
import os
import json
import tempfile

VALID_GASD = 'CONTEXT: "TestCLI"\nTARGET: "Python3"\nTYPE MyT:\n  f: String\n'
INVALID_GASD = "NOT VALID GASD SYNTAX AT ALL ::::: {{{{"

# The project root — pytest is always invoked from here
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None):
    """Helper to invoke the CLI and return the result."""
    if file_path is None:
        tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
        tmp.write(input_content or VALID_GASD)
        tmp.close()
        file_path = tmp.name

    result = subprocess.run(
        ["python3", "-m", "Impl.cli", file_path, *args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, file_path


def test_semast_cli_activation():
    """ENSURE '--ast-sem --json flag activates semantic AST output'"""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert "asts" in data
        assert data["asts"][0]["kind"] == "SemanticSystem"
        # No status message on stderr when using --json
        assert result.stderr == ""
    finally:
        os.unlink(fp)


def test_semast_cli_silent_without_json():
    """ENSURE '--ast-sem' alone does not print JSON to stdout"""
    result, fp = run_cli("--ast-sem")
    try:
        assert result.returncode == 0
        assert "OK" in result.stderr
        assert result.stdout.strip() == ""
    finally:
        os.unlink(fp)


def test_semast_cli_dual_output():
    """ENSURE '--ast-sem produces semantic AST with namespaces key'"""
    result, fp = run_cli("--ast-sem", "--json")
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        output = data["asts"][0]
        # Semantic AST has namespaces, regular AST does not
        assert "namespaces" in output
    finally:
        os.unlink(fp)


def test_semast_cli_output_dir():
    """ENSURE '--ast-output writes semantic AST JSON to a file'"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name
    
    result, fp = run_cli("--ast-sem", "--ast-output", out_path)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert os.path.exists(out_path)
        with open(out_path) as f:
            data = json.load(f)
        assert data["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_semast_cli_combine():
    """ENSURE '--ast-combine produces a combined JSON array for multiple files'"""
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write('CONTEXT: "C1"\nTARGET: "P"\nTYPE T1:\n  f: String\n')
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write('CONTEXT: "C2"\nTARGET: "P"\nTYPE T2:\n  g: Integer\n')
    tmp2.close()

    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast-sem", "--ast-combine", "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        output = data["asts"]
        assert isinstance(output, list)
        # In Ph4, --ast-sem with multiple files produces 1 unified SemanticSystem
        assert len(output) == 1
        assert output[0]["kind"] == "SemanticSystem"
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)


def test_semast_cli_errors():
    """ENSURE 'CLI returns exit code 1 on parse errors and does not produce semantic AST'"""
    result, fp = run_cli("--ast-sem", input_content=INVALID_GASD)
    try:
        assert result.returncode == 1
        # Should not produce valid JSON on stdout for invalid input
        assert "SemanticSystem" not in result.stdout
    finally:
        os.unlink(fp)


def test_semast_cli_default_behavior():
    """ENSURE 'Without --ast-sem, default output shows OK/FAIL summary'"""
    result, fp = run_cli()
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        # Default behavior: status messages on stderr
        assert "OK" in result.stderr
    finally:
        os.unlink(fp)


def test_semast_cli_combined_opts():
    """ENSURE '--ast-sem --json produces a JSON wrapper with success field'"""
    result, fp = run_cli("--json")
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["success"] is True
    finally:
        os.unlink(fp)


def test_semast_cli_regression_missing_file():
    """ENSURE 'CLI handles missing file gracefully with exit code 1'"""
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", "nonexistent_file_12345.gasd", "--ast-sem"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    assert result.returncode == 1
    assert "not found" in result.stderr.lower() or "error" in result.stderr.lower()

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_cli_multi_file():
    # AT-X-SEMAST-010-01, AC-X-SEMAST-010-01
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write('CONTEXT: "Multi"\nTARGET: "Py"\nTYPE T1: f: String\n')
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write('CONTEXT: "Multi"\nTARGET: "Py"\nTYPE T2: g: Integer\n')
    tmp2.close()

    try:
        # ENSURE "The CLI accepts a list of files and produces a single unified Semantic AST"
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast-sem", "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        # In unified mode (without --ast-combine), it should return 1 SemanticSystem
        assert len(data["asts"]) == 1
        system = data["asts"][0]
        assert "global" in system["namespaces"]
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)

def test_semast_cli_deterministic_errors():
    # AT-X-SEMAST-010-02, AC-X-SEMAST-010-02
    # Create two files that both have semantic errors
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write('CONTEXT: "Err"\nTARGET: "Py"\nTYPE T1: f: MissingType\n')
    tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write('CONTEXT: "Err"\nTARGET: "Py"\nTYPE T2: g: AnotherMissingType\n')
    tmp2.close()

    try:
        results = []
        for _ in range(3):
            result = subprocess.run(
                ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast-sem"],
                capture_output=True, text=True,
                env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
                cwd=PROJECT_ROOT
            )
            results.append(result.stderr)
        
        # ENSURE "Error reporting order is deterministic regardless of filesystem OS order"
        assert results[0] == results[1] == results[2]
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)

def test_cli_version_build_time():
    """ENSURE '--version' returns the version and build time string."""
    # Note: When running from source, this will be "DEVELOPMENT"
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", "--version"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    assert result.returncode == 0
    assert result.stdout.strip() != ""
    # In development it should be "DEVELOPMENT", but might be a real timestamp
    assert "gasd_parser" in result.stdout
    assert "built:" in result.stdout
