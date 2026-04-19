import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.ast.ASTNodes import GASDFile

def test_ast_snapshot_consistency():
    """RT-PARSER-003-01: Existing AST snapshots remain consistent."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Snapshot"
TARGET: "Python3"
TYPE T:
    f: String
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    # Check stable fields that shouldn't change across versions
    assert ast.kind == "GASDFile"
    assert len(ast.types) == 1
    assert ast.types[0].name == "T"
    assert ast.types[0].fields[0].name == "f"
    assert ast.types[0].fields[0].type.baseType == "String"

def test_ast_backward_compatibility():
    """RT-PARSER-003-02: AST schema backward compatibility maintained."""
    api = ParseTreeAPI()
    content = """CONTEXT: "BackCompat"
TARGET: "Python3"
COMPONENT C:
    INTERFACE:
        run(id: Integer) -> Boolean
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    # Verify all established AST fields still exist and work
    assert hasattr(ast, 'kind')
    assert hasattr(ast, 'components')
    assert hasattr(ast, 'types')
    assert hasattr(ast, 'flows')
    assert hasattr(ast, 'strategies')
    assert hasattr(ast, 'constraints')
    assert hasattr(ast, 'line')
    assert hasattr(ast, 'column')
    
    # Verify component schema stability
    comp = ast.components[0]
    assert hasattr(comp, 'name')
    assert hasattr(comp, 'methods')
    assert hasattr(comp, 'pattern')
    assert hasattr(comp, 'dependencies')
    assert comp.methods[0].parameters[0].name == "id"
