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

@pytest.mark.parametrize("case_id, content, expected_exit, expected_error", [
    # 1. VERSION (AT-V2-101)
    ("AT-V2-101", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\n", 0, ""),
    
    # 2. ACHIEVE - Mandatory POSTCONDITION (AT-V2-102, 103)
    ("AT-V2-102", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'Task'\n", 1, "LINT-001"),
    ("AT-V2-103", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nFLOW f():\n  1. ACHIEVE 'Task'\n    POSTCONDITION: result IS UUID\n", 0, ""),
    
    # 3. IMPORT - Mandatory CONTRACT (AT-V2-104, 105)
    ("AT-V2-104", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nIMPORT 'External'\n", 1, "LINT-002"),
    ("AT-V2-105", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nCONTRACT 'C':\n  CASE 'Valid':\n    POSTCONDITION: true\n", 0, ""),
    
    # 4. CONTRACT CASE - Outcome required (AT-V2-106)
    ("AT-V2-106", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nCONTRACT 'C':\n  CASE 'Invalid':\n    ENSURE 'No Outcome'\n", 1, "LINT-007"),
    
    # 5. DEPENDS_ON - Semantic Checks (AT-V2-107, 108)
    ("AT-V2-107", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nFLOW f():\n  1. ACHIEVE 'T1'\n  2. ACHIEVE 'T2'\n    DEPENDS_ON STEP 'NonExistent'\n    POSTCONDITION: true\n", 1, "LINT-008"),
    ("AT-V2-108", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nFLOW f():\n  1. ACHIEVE 'T1'\n    DEPENDS_ON STEP 'T2'\n    POSTCONDITION: true\n  2. ACHIEVE 'T2'\n    DEPENDS_ON STEP 'T1'\n    POSTCONDITION: true\n", 1, "LINT-009"),
    
    # 6. INVARIANT - Scope required (AT-V2-109)
    ("AT-V2-109", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nINVARIANT 'Inv': true\n", 1, "LINT-003"),
    
    # 7. GLOBAL INVARIANT - Enforcement (AT-V2-110)
    ("AT-V2-110", "VERSION 1.2\nNAMESPACE: 'Test'\nTARGET: 'Python'\nGLOBAL INVARIANT 'Inv': counts > 0\n", 0, "LINT-006"),
    
    # 8. ANNOTATION IDs (AT-V2-111, 112, 113)
    ("AT-V2-111", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\n@retry(3)\nTYPE T: s: String\n", 1, "LINT-011"),
    ("AT-V2-112", "@retry(3) AS 'lower'\nVERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nTYPE T: s: String\n", 1, "ERROR"),
    ("AT-V2-113", "@retry(3) AS 'R1'\n@timeout(10) AS 'R1'\nVERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\nTYPE T: s: String\n", 1, "LINT-010"),
    
    # 9. ENVIRONMENTAL DEPENDENCIES (AT-V2-114, 115, 117)
    ("AT-V2-114", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\n@transaction_type('ACID') AS 'TX'\nTYPE T: s: String\n", 1, "LINT-005"),
    ("AT-V2-115", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\n@retry(3) AS 'R'\nTYPE T: s: String\n", 1, "LINT-004"),
    ("AT-V2-117", "VERSION 1.2\nNAMESPACE: 'T'\nTARGET: 'P'\n@circuit_breaker AS 'CB'\n@idempotent AS 'ID'\nTYPE T: s: String\nASSUMPTION 'CB works'\n", 0, ""),
])
def test_v2_acceptance_comprehensive(run_cli, case_id, content, expected_exit, expected_error):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, f"{case_id}.gasd")
        create_gasd(file_path, content)
        exit_code, stdout, stderr = run_cli([file_path, "--ast-sem"])
        assert exit_code == expected_exit, f"Failed {case_id}: exit code mismatch ({exit_code} != {expected_exit}). STDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        if expected_error:
            if expected_error not in stderr and expected_error not in stdout:
                 print(f"\nSTDOUT ({case_id}):\n{stdout}")
                 print(f"STDERR ({case_id}):\n{stderr}")
            assert expected_error in stderr or expected_error in stdout, f"Failed {case_id}: missing expected error {expected_error}"
