import pytest
import os
import tempfile
import sys
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

@pytest.mark.parametrize("case_id, content, expected_exit, expected_error, cli_args", [
    # 1. ACHIEVE without POSTCONDITION in 1.2
    ("NEG-L001", "VERSION 1.2\nNAMESPACE: 'T'\nFLOW f():\n  1. ACHIEVE 'T'\n", 1, "LINT-001", ["--ast-sem"]),
    
    # 2. IMPORT without CONTRACT in 1.2
    ("NEG-L002", "VERSION 1.2\nNAMESPACE: 'T'\nIMPORT 'Ext'\n", 1, "LINT-002", ["--ast-sem"]),
    
    # 3. Annotation without AS in 1.2
    ("NEG-L011", "VERSION 1.2\nNAMESPACE: 'T'\n@retry(3)\nTYPE T: s: String\n", 1, "LINT-011", ["--ast-sem"]),
    
    # 4. Legacy --ast flag
    ("NEG-AST", "VERSION 1.2\nNAMESPACE: 'T'\n", 1, "Unknown argument", ["--ast"]),
    
    # 5. Version mismatch (LINT-013)
    ("NEG-VER", "CONTEXT: 'T'\nTARGET: 'P'\nVERSION 1.1\nNAMESPACE: 'T'\nTYPE T: s: String\n", 1, "LINT-013", ["--gasd-ver", "1.2", "--ast-sem"]),
    
    # 6. Invalid VERSION placement (not at top)
    ("NEG-PLACE", "NAMESPACE: 'T'\nVERSION 1.2\n", 1, "SyntaxError", ["--ast-sem"]),
])
def test_v2_negative_scenarios(run_cli, case_id, content, expected_exit, expected_error, cli_args):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{case_id}.gasd")
        create_gasd(file_path, content)
        exit_code, stdout, stderr = run_cli([file_path] + cli_args)
        assert exit_code == expected_exit, f"Failed {case_id}: exit code mismatch"
        assert expected_error.lower() in (stderr + stdout).lower(), f"Failed {case_id}: missing expected error {expected_error}"
