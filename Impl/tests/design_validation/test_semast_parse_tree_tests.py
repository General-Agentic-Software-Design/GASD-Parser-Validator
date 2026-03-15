import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_parse_tree_to_ast_mapping():
    """Validates full coverage of ParseTree to AST mapping."""
    content = """CONTEXT: "Test"
TARGET: "T"

TYPE T:
    f: S

COMPONENT C:
    INTERFACE:
        m() -> V

FLOW F():
    1. ACHIEVE "X"

DECISION "D":
    CHOSEN: "A"
"""
    api = ParseTreeAPI()
    tree, reporter = api.parse(content)
    assert not reporter.has_errors(), f"Errors: {[e.message for e in reporter.syntax_errors]}"
    ast = ASTGenerator().visit(tree)
    assert len(ast.types) == 1
    assert len(ast.components) == 1
    assert len(ast.flows) == 1
    assert len(ast.decisions) == 1
