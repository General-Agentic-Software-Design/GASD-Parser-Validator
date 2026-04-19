import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Regression Test for GEP-5: Explicit Binding Stability
@trace #RT-VALIDATE-001, #RT-VALIDATE-002
"""

def test_binding_enforcement_stability():
    """RT-VALIDATE-001: Ensure no regression allows implicit binding."""
    content = """CONTEXT: "Regres"
TARGET: "P"
FLOW F():
    1. VALIDATE user  # Old invalid syntax
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() > 0, "Regression: Implicit binding was incorrectly accepted"

def test_binding_resolution_stability():
    """RT-VALIDATE-002: Ensure complex path resolution remains stable."""
    content = """CONTEXT: "Regres"
TARGET: "P"
TYPE User:
    addr: Address
TYPE Address:
    zip: String
FLOW F():
    1. VALIDATE a AS TYPE.Address
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
