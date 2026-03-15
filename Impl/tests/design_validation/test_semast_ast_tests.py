import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_ast_node_mapping():
    """Validates AC-PARSER-002-01: Correct mapping of ParseTree to AST."""
    content = 'CONTEXT: "Test"\nTARGET: "Python"\nTYPE T: f: String\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    assert ast.kind == "GASDFile"
    assert len(ast.types) == 1
    assert ast.types[0].name == "T"

def test_ast_directive_parsing():
    """Validates AC-PARSER-002-02: Parsing of top-level directives."""
    content = 'CONTEXT: "Test"\nTARGET: "Python", "TypeScript"\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    directives = {d.directiveType: d.values for d in ast.directives}
    assert '"Test"' in directives["CONTEXT"]
    assert '"Python"' in directives["TARGET"]
    assert '"TypeScript"' in directives["TARGET"]
