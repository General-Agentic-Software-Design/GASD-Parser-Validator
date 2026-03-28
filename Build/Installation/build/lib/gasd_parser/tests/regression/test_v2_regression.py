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

@pytest.mark.parametrize("case_id, content, expected_exit", [
    ("RT-V2-201", "VERSION 1.2\nCONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\n", 0),
    ("RT-V2-202", "VERSION 1.1\nCONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'Task'\n", 0), # Default ACHIEVE OK in 1.1
    ("RT-V2-203", "VERSION 1.1\nCONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\nINVARIANT 'Inv': true\n", 0), # Local INVARIANT OK in 1.1 (deprecated warning only)
    ("RT-V2-204", "VERSION 1.1\nCONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'T'\n  2. ENSURE 'ID generated'\n", 0),
    ("RT-V2-205", "CONTEXT: 'Test'\nNAMESPACE: 'Test'\nTARGET: 'Python'\nTYPE T: s: String\n", 0), # EBNF compatibility
    ("RT-V2-206", "VERSION 1.1\nCONTEXT: 'T'\nNAMESPACE: 'T'\nTARGET: 'P'\n@retry(3)\nTYPE T: s: String\n", 0), # 1.1 doesn't require AS ID
])
def test_v2_regression_comprehensive(run_cli, case_id, content, expected_exit):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{case_id}.gasd")
        create_gasd(file_path, content)
        exit_code, stdout, stderr = run_cli([file_path, "--ast-sem"])
        assert exit_code == expected_exit
        if case_id in ["RT-V2-202", "RT-V2-203"]:
            # These should be warnings in 1.1 but errors in 1.2
            assert "WARNING" in (stdout + stderr) or "Warning" in (stdout + stderr)
