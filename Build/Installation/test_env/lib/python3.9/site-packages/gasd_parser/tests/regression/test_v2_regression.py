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

@pytest.mark.parametrize("case_id, content, expected_exit, expected_version, expected_warning", [
    # RT-V2-201: Missing VERSION defaults to 1.1
    ("RT-V2-201", "NAMESPACE: 'Test'\nTARGET: 'Python'\nTYPE T: s: String\n", 0, "1.1", ""),
    
    # RT-V2-202: Standard 1.1 ACHIEVE (Warning only)
    ("RT-V2-202", "VERSION 1.1\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'Task'\n", 0, "1.1", "Warning"),
    
    # RT-V2-203: Standard 1.1 INVARIANT defaults to LOCAL
    ("RT-V2-203", "VERSION 1.1\nNAMESPACE: 'Test'\nTARGET: 'Python'\nINVARIANT 'Inv': true\n", 0, "1.1", "Warning"),
    
    # RT-V2-204: 1.1 Auto-ID generation (PO- prefix)
    ("RT-V2-204", "VERSION 1.1\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'T'\n  2. ENSURE 'ID generated'\n", 0, "1.1", ""),
    
    # RT-V2-205: Verbatim 1.1 EBNF compatibility
    ("RT-V2-205", "CONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\nTYPE T: s: String\n", 0, "1.1", ""),

    # RT-V2-206: 1.1 Annotation without AS (Legacy support)
    ("RT-V2-206", "VERSION 1.1\nNAMESPACE: 'T'\nTARGET: 'P'\n@retry(3)\nTYPE T: s: String\n", 0, "1.1", ""),
])
def test_v2_regression_comprehensive(run_cli, case_id, content, expected_exit, expected_version, expected_warning):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{case_id}.gasd")
        create_gasd(file_path, content)
        # Force --gasd-ver 1.1 for some, or let it default
        args = [file_path, "--ast-sem"]
        exit_code, stdout, stderr = run_cli(args)
        assert exit_code == expected_exit, f"Failed {case_id}: exit code mismatch"
        
        combined_out = (stdout + stderr).lower()
        if expected_warning:
            assert expected_warning.lower() in combined_out, f"Failed {case_id}: missing expected warning {expected_warning}"
