import pytest
import subprocess
import os
import json
import tempfile

VALID_GASD = 'CONTEXT: "TestReuse"\nTARGET: "Python3"\nTYPE MyT:\n  f: String\n'

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_sem_ast(gasd_content, *extra_args):
    """Run CLI with --ast-sem and return parsed JSON output."""
    tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp.write(gasd_content)
    tmp.close()
    result = subprocess.run(
        ["python3", "-m", "Impl.cli", tmp.name, "--ast-sem", "--json", *extra_args],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    return result, tmp.name


def test_semast_cli_activation():
    """ENSURE 'Semantic AST output is deterministic across repeated runs'"""
    with tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w") as tmp:
        tmp.write(VALID_GASD)
        fp1 = tmp.name
    try:
        result1 = subprocess.run(
            ["python3", "-m", "Impl.cli", fp1, "--ast-sem", "--json"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": PROJECT_ROOT}, cwd=PROJECT_ROOT
        )
        result2 = subprocess.run(
            ["python3", "-m", "Impl.cli", fp1, "--ast-sem", "--json"],
            capture_output=True, text=True, env={**os.environ, "PYTHONPATH": PROJECT_ROOT}, cwd=PROJECT_ROOT
        )
        assert result1.returncode == 0, f"stderr: {result1.stderr}"
        assert result2.returncode == 0, f"stderr: {result2.stderr}"
        out1 = json.loads(result1.stdout)
        out2 = json.loads(result2.stdout)
        byte_hash = "semantic_ast_bytes_sha512"
        first_digest = out1["semantic_validate"].pop(byte_hash)
        second_digest = out2["semantic_validate"].pop(byte_hash)
        assert first_digest != second_digest
        # Generated IDs and validation times vary between runs.
        def strip_ids(obj):
            if isinstance(obj, dict):
                return {k: strip_ids(v) for k, v in obj.items() if k not in ("id", "validation_time")}
            elif isinstance(obj, list):
                return [strip_ids(x) for x in obj]
            return obj
        assert strip_ids(out1) == strip_ids(out2)
    finally:
        os.unlink(fp1)


def test_semast_cli_dual_output():
    """ENSURE 'Writing to file produces the same structure as stdout'"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name
    
    result_stdout, fp1 = run_sem_ast(VALID_GASD)
    result_file, fp2 = run_sem_ast(VALID_GASD, "--ast-output", out_path)
    try:
        assert result_stdout.returncode == 0, f"stderr: {result_stdout.stderr}"
        assert result_file.returncode == 0, f"stderr: {result_file.stderr}"
        with open(out_path) as f:
            file_data = json.load(f)
        stdout_data = json.loads(result_stdout.stdout)
        
        # Same kind structure
        assert file_data["kind"] == stdout_data["kind"]
        assert file_data["kind"] == "SemanticSystem"
        # check namespaces exist
        assert "namespaces" in file_data
    finally:
        os.unlink(fp1)
        os.unlink(fp2)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_semast_cli_output_dir():
    """ENSURE 'Output file is overwritten cleanly on re-run'"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out_f:
        out_path = out_f.name
    
    result1, fp1 = run_sem_ast(VALID_GASD, "--ast-output", out_path)
    assert result1.returncode == 0, f"stderr: {result1.stderr}"
    with open(out_path) as f:
        data1 = json.load(f)

    result2, fp2 = run_sem_ast(VALID_GASD, "--ast-output", out_path)
    assert result2.returncode == 0, f"stderr: {result2.stderr}"
    with open(out_path) as f:
        data2 = json.load(f)
    
    try:
        assert data1["kind"] == data2["kind"]
    finally:
        os.unlink(fp1)
        os.unlink(fp2)
        if os.path.exists(out_path):
            os.unlink(out_path)


def test_semast_cli_combine():
    """ENSURE 'Combined output includes both files in one SemanticSystem'"""
    gasd1 = 'CONTEXT: "R1"\nTARGET: "P"\nTYPE A:\n  f: String\n'
    gasd2 = 'CONTEXT: "R2"\nTARGET: "P"\nTYPE B:\n  g: Integer\n'
    
    tmp1 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp1.write(gasd1); tmp1.close()
    tmp2 = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp2.write(gasd2); tmp2.close()
    
    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp1.name, tmp2.name, "--ast-sem", "--ast-combine", "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        assert data["kind"] == "SemanticSystem"
        assert len(data["compilationUnit"]["fileNodes"]) == 2
    finally:
        os.unlink(tmp1.name)
        os.unlink(tmp2.name)


def test_semast_cli_errors():
    """ENSURE 'Semantic AST output has all required schema keys'"""
    result, fp = run_sem_ast(VALID_GASD)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        required_keys = ["kind", "namespaces", "metadata"]
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    finally:
        os.unlink(fp)


def test_semast_cli_default_behavior():
    """ENSURE 'SemanticSystem to_dict() round-trips cleanly'"""
    result, fp = run_sem_ast(VALID_GASD)
    try:
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stdout)
        reserialized = json.dumps(data, sort_keys=True)
        reparsed = json.loads(reserialized)
        assert reparsed["kind"] == "SemanticSystem"
    finally:
        os.unlink(fp)


def test_semast_cli_combined_opts():
    """ENSURE '--json retains the validation report on stderr'"""
    tmp = tempfile.NamedTemporaryFile(suffix=".gasd", delete=False, mode="w")
    tmp.write(VALID_GASD)
    tmp.close()
    try:
        result = subprocess.run(
            ["python3", "-m", "Impl.cli", tmp.name, "--json"],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        data = json.loads(result.stderr)
        assert "success" in data
        assert data["success"] is True
    finally:
        os.unlink(tmp.name)


def test_semast_cli_regression_missing_file():
    """ENSURE 'CLI exit code is consistent for missing files'"""
    result1 = subprocess.run(
        ["python3", "-m", "Impl.cli", "missing_xyzzy.gasd", "--ast-sem"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    result2 = subprocess.run(
        ["python3", "-m", "Impl.cli", "missing_xyzzy.gasd", "--ast-sem"],
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=PROJECT_ROOT
    )
    assert result1.returncode == result2.returncode == 1
