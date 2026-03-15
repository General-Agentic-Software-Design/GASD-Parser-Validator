import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Design Validation: Grammar
Mapped from Validation/grammar_tests.gasd
"""

def test_design_grammar_valid_file():
    """FLOW test_grammar_valid_file"""
    content = 'CONTEXT: "Design"\nTARGET: "P"\n'
    api = ParseTreeAPI()
    _, errors = api.parse(content)
    if errors.get_error_count() > 0:
        print(f"DEBUG ERRORS (valid_file): {errors.to_console()}")
    assert errors.get_error_count() == 0

def test_design_grammar_missing_keyword():
    """FLOW test_grammar_missing_keyword"""
    content = 'CONTEXT "MissingColon"\n'
    api = ParseTreeAPI()
    _, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_design_validate_missing_binding():
    """FLOW test_validate_missing_binding (GEP-5)"""
    content = 'CONTEXT: "G"\nTARGET: "P"\nFLOW F(): 1. VALIDATE user\n'
    api = ParseTreeAPI()
    _, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_design_validate_complex_path():
    """FLOW test_validate_complex_path (GEP-5)"""
    content = 'CONTEXT: "G"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE a AS TYPE.U.A\n'
    api = ParseTreeAPI()
    _, errors = api.parse(content)
    if errors.get_error_count() > 0:
        print(f"DEBUG ERRORS (complex_path): {errors.to_console()}")
    assert errors.get_error_count() == 0
