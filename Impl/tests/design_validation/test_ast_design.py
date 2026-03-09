import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

"""
Design Validation: AST
Mapped from Validation/ast_tests.gasd
"""

def test_design_ast_validate_binding():
    """FLOW test_ast_validate_binding (GEP-5)"""
    content = 'CONTEXT: "G"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE u AS TYPE.User\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    step = ast.flows[0].steps[0]
    assert step.action == "VALIDATE"
    assert step.asBinding == "AS TYPE"
    assert step.typePath == "User"

def test_design_ast_metadata():
    """FLOW test_ast_metadata"""
    api = ParseTreeAPI()
    tree, _ = api.parse("TYPE T: f: S\n")
    ast = ASTGenerator().visit(tree)
    assert ast.types[0].line == 1
