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
    # NT-GEP6-001: Missing Step Reference
    ("NT-GEP6-001", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\nFLOW f():\n  1. ACHIEVE 'T1'\n    DEPENDS_ON STEP 'Missing'\n    POSTCONDITION: true\n", 1),
    
    # NT-GEP6-002: Circular Dependency
    ("NT-GEP6-002", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\nFLOW f():\n  1. ACHIEVE 'T1'\n    DEPENDS_ON STEP 'T1'\n    POSTCONDITION: true\n", 1),
    
    # NT-GEP6-003: AS ID Collision
    ("NT-GEP6-003", "@retry(3) AS 'ID'\n@timeout(1) AS 'ID'\nVERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\n", 1),
    
    # NT-GEP6-004: Missing Outcome in Case
    ("NT-GEP6-004", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\nCONTRACT 'C':\n  CASE 'X':\n    ENSURE 'NoOutcome'\n", 1),
    
    # NT-GEP6-005: Regex Violation for AS ID
    ("NT-GEP6-005", "@retry(3) AS 'lower_case'\nVERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\n", 1),
    
    # NT-GEP6-006: Top-level Postcondition violation
    ("NT-GEP6-006", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\nPOSTCONDITION: outside_achieve == true\n", 1),
    
    # NT-GEP6-007: Version Mismatch in Imports (LINT-012 INFO, success)
    ("NT-GEP6-007", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nCONTEXT: 'I'\nIMPORT 'legacy.gasd'\n", 0), # Now INFO (LINT-012) — success
])
def test_v2_negative_comprehensive(run_cli, case_id, content, expected_exit):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{case_id}.gasd")
        if case_id == "NT-GEP6-007":
            # Create a VALID legacy file
            create_gasd(os.path.join(tmpdir, "legacy.gasd"), "NAMESPACE: 'Legacy'\nTARGET: 'P'\nCONTEXT: 'I'\nTYPE T: s: String\n")
            
        create_gasd(file_path, content)
        exit_code, stdout, stderr = run_cli([file_path, "--ast-sem"])
        assert exit_code == expected_exit
        if case_id == "NT-GEP6-007":
            assert "LINT-012" in stderr or "LINT-012" in stdout
        elif case_id == "NT-GEP6-006":
            # Top-level POSTCONDITION is rejected by the parser as a SYNTAX error
            assert "SYNTAX" in (stdout + stderr) or "POSTCONDITION" in (stdout + stderr)
        else:
            assert any(f"LINT-00{i}" in (stdout + stderr) or f"LINT-01{i}" in (stdout + stderr) for i in range(13))
