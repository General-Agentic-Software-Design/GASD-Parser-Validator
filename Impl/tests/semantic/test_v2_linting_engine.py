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

@pytest.mark.parametrize("rule_id, v11_content, v12_content, expected_v11_exit, expected_v12_exit", [
    # LINT-001: ACHIEVE without POSTCONDITION
    ("LINT-001", 
     "VERSION 1.1\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nFLOW f():\n  1. ACHIEVE 'T'\n", 
     "VERSION 1.2\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nFLOW f():\n  1. ACHIEVE 'T'\n", 
     0, 1), # Warning in 1.1 (Success), Error in 1.2 (Failure)
    
    # LINT-002: IMPORT without CONTRACT
    ("LINT-002", 
     "VERSION 1.1\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nIMPORT 'Ext'\n", 
     "VERSION 1.2\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nIMPORT 'Ext'\n", 
     0, 1),
    
    # LINT-003: INVARIANT without scope
    ("LINT-003", 
     "VERSION 1.1\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nINVARIANT 'I': true\n", 
     "VERSION 1.2\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\nINVARIANT 'I': true\n", 
     0, 1), # Info/Warning in 1.1, Error in 1.2
     
    # LINT-011: Annotation without AS
    ("LINT-011", 
     "VERSION 1.1\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\n@retry(3)\nTYPE T: s: String\n", 
     "VERSION 1.2\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\n@retry(3)\nTYPE T: s: String\n", 
     0, 1),
    
    # LINT-013: VERSION_MISMATCH (requires --gasd-ver to trigger)
    ("LINT-013", 
     "VERSION 1.1\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\n", 
     "VERSION 1.2\nCONTEXT: 'T'\nTARGET: 'P'\nNAMESPACE: 'T'\n", 
     1, 1), # Fails if CLI version is overridden to mismatched version
])
def test_lint_rules_severity_v11_vs_v12(run_cli, rule_id, v11_content, v12_content, expected_v11_exit, expected_v12_exit):
    """
    Verify GEP-6 lint rules (LINT-001 to LINT-013) with version-sensitive severity.
    As defined in Validation/Linting/linting_validation.gasd.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # V1.1 Check
        f11 = os.path.join(tmpdir, "v11.gasd")
        create_gasd(f11, v11_content)
        if rule_id == "LINT-013":
            # LINT-013 needs --gasd-ver to trigger: v1.1 file with --gasd-ver 1.2
            exit11, out11, err11 = run_cli([f11, "--ast-sem", "--gasd-ver", "1.2"])
        else:
            exit11, out11, err11 = run_cli([f11, "--ast-sem"])
        assert exit11 == expected_v11_exit, f"Rule {rule_id} failed v11 check"
        if expected_v11_exit == 0 and rule_id in ["LINT-001", "LINT-002", "LINT-003", "LINT-011"]:
             assert "Warning" in (out11 + err11) or "WARNING" in (out11 + err11)
        
        # V1.2 Check
        f12 = os.path.join(tmpdir, "v12.gasd")
        create_gasd(f12, v12_content)
        if rule_id == "LINT-013":
            # LINT-013 needs --gasd-ver to trigger: v1.2 file with --gasd-ver 1.1
            exit12, out12, err12 = run_cli([f12, "--ast-sem", "--gasd-ver", "1.1"])
        else:
            exit12, out12, err12 = run_cli([f12, "--ast-sem"])
        assert exit12 == expected_v12_exit, f"Rule {rule_id} failed v12 check"
        if expected_v12_exit == 1:
             assert rule_id in (out12 + err12)

