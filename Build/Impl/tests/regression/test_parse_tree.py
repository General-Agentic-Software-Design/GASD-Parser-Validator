import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_ast_structure_stability():
    """RT-PARSER-002-01: AST structure remains stable across parser versions."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Stable"
TARGET: "Python3"
TYPE T:
    f: String
COMPONENT C:
    INTERFACE:
        m() -> Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    assert tree is not None
    # Verify fundamental structure hasn't changed
    sections = [tree.section(i) for i in range(tree.getChildCount()) if tree.section(i)]
    assert any(s.context_dir() is not None for s in sections), "CONTEXT section missing"
    assert any(s.target_dir() is not None for s in sections), "TARGET section missing"
    assert any(s.type_def() is not None for s in sections), "TYPE section missing"
    assert any(s.component_def() is not None for s in sections), "COMPONENT section missing"

def test_parse_tree_stability():
    """RT-PARSER-002-02: Tree generation works for all existing cases."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Stability"
TARGET: "Python3"
COMPONENT C:
    INTERFACE:
        m() -> Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    assert tree is not None
    # Ensure standard hierarchy
    assert tree.section(0).context_dir() is not None
    assert tree.section(2).component_def() is not None
