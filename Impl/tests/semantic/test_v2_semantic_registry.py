import pytest
import os
import tempfile
import sys
import json
from Impl.cli import main
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

@pytest.fixture
def run_cli():
    def _run(args):
        stdout = StringIO()
        stderr = StringIO()
        exit_code = 0
        original_argv = sys.argv
        sys.argv = ["gasd-parser"] + args
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                main()
        except SystemExit as e:
            exit_code = e.code
        finally:
            sys.argv = original_argv
        return exit_code, stdout.getvalue(), stderr.getvalue()
    return _run

def create_gasd(path, content):
    with open(path, "w") as f:
        f.write(content)

@pytest.mark.parametrize("annotation, triple_check", [
    ("@range(1, 10)", "structural,runtime"),
    ("@min_length(5)", "structural"),
    ("@max_length(50)", "structural"),
    ("@format('email')", "structural"),
    ("@unique('GLOBAL')", "environmental"),
    ("@default('foo')", "structural"),
    ("@constraint('Must be prime')", "runtime"),
    ("@injectable", "environmental"),
    ("@mockable", "structural"),
    ("@transaction_type('ACID')", "environmental"),
    ("@transaction_type('SAGA')", "runtime"),
    ("@async", "environmental"),
    ("@retry(3)", "runtime"),
    ("@timeout(100)", "environmental"),
    ("@external", "runtime"),
    ("@hash('SHA256')", "structural"),
    ("@circuit_breaker", "runtime"),
    ("@cacheable(60)", "environmental"),
    ("@idempotent", "runtime"),
    ("@sensitive", "environmental"),
    ("@authorized('admin')", "environmental"),
])
def test_v2_semantic_registry_standard_annotations(run_cli, annotation, triple_check):
    """
    Verify all 21 standard annotations from Validation/SemanticRegistry/registry_validation.gasd.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Construct a valid GASD file with the annotation
        # Add @idempotent if testing @retry to satisfy LINT-004
        content = f"VERSION 1.2\nNAMESPACE: 'T'\n"
        if "@retry" in annotation:
             content += "@idempotent AS 'I1'\n"
        content += f"{annotation} AS 'A1'\nTYPE T: s: String\n"
        
        if "environmental" in triple_check:
             # Use the alias 'A1' in the assumption name to satisfy Linter's link check
             content += "ASSUMPTION 'A1 environmental check'\n"
        
        file_path = os.path.join(tmpdir, "registry_test.gasd")
        create_gasd(file_path, content)
        
        # In Ph3, we verify it is accepted.
        # In Ph4, we will verify the registry metadata via --json
        exit_code, stdout, stderr = run_cli([file_path, "--ast-sem", "--json"])
        assert exit_code == 0, f"Annotation {annotation} failed: {stderr}"
