import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Design Validation: Parse Tree
Mapped from Validation/parse_tree_tests.gasd
"""

def test_design_parse_tree_root():
    """FLOW test_parse_tree_root"""
    api = ParseTreeAPI()
    tree, _ = api.parse("CONTEXT: 'D'\nTARGET: 'P'\n")
    # Validates that root is correct context
    assert "Gasd_fileContext" in str(type(tree))

def test_design_parse_tree_order():
    """FLOW test_parse_tree_order"""
    api = ParseTreeAPI()
    tree, _ = api.parse("TYPE A: f: S\nTYPE B: f: S\n")
    # Check text or node order
    assert "A" in tree.section(0).getText()
    assert "B" in tree.section(1).getText()
