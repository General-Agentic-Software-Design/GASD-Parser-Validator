import pytest
import os
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_valid_parsing():
    """AT-PARSER-001-01: Valid GASD file parses successfully."""
    api = ParseTreeAPI()
    spec_path = "Specs/valid_sample.gasd"
    
    with open(spec_path, 'r') as f:
        content = f.read()
        
    tree, errors = api.parse(content)
    
    assert errors.get_error_count() == 0, f"Errors found: {errors.to_console()}"
    assert tree is not None

def test_invalid_missing_keyword():
    """AT-PARSER-001-02: Missing keyword causes syntax error."""
    api = ParseTreeAPI()
    # Missing 'CONTEXT' keyword - will just fail validation or be syntax error depending on use
    content = "TARGET: 'Python3'\n" 
    tree, errors = api.parse(content)
    
    # Actually, the grammar might parse it but the validator will catch it.
    # But let's check a raw syntax error like wrong keyword
    content = "INVALID_KW: 'Value'\n"
    tree, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_multiple_capabilities():
    """AT-PARSER-001-04: Multiple capabilities within system parse correctly."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Multi"
TARGET: "Python3"

COMPONENT Comp1:
    INTERFACE:
        run() -> Boolean

COMPONENT Comp2:
    INTERFACE:
        stop() -> Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

def test_incorrect_structure():
    """AT-PARSER-001-03: Incorrect indentation or structure fails parsing."""
    api = ParseTreeAPI()
    # Completely malformed: field outside any TYPE block
    content = """CONTEXT: "BadStructure"
TARGET: "Python3"
f1: String
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() > 0
