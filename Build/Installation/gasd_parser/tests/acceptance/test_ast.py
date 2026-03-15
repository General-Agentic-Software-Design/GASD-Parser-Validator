import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.ast.ASTNodes import GASDFile

def test_ast_generation_valid():
    """AT-PARSER-003-01: AST is correctly generated from a valid parse tree."""
    api = ParseTreeAPI()
    spec_path = "Specs/valid_sample.gasd"
    
    with open(spec_path, 'r') as f:
        content = f.read()
        
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator(source_file=spec_path)
    ast = generator.visit(tree)
    
    assert isinstance(ast, GASDFile)
    assert len(ast.types) > 0
    assert len(ast.components) > 0
    assert len(ast.flows) > 0

def test_ast_location_metadata():
    """AT-PARSER-003-01: Every AST node contains source location metadata."""
    api = ParseTreeAPI()
    content = 'CONTEXT: "LocTest"\nTARGET: "Python3"\nTYPE T:\n  f: String\n'
    tree, errors = api.parse(content)
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    assert ast.line == 1
    assert ast.types[0].line == 3
    assert ast.types[0].fields[0].line == 4

def test_ast_hierarchy():
    """AT-PARSER-003-02: Capabilities (Components) appear under System (GASDFile)."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Hierarchy"
TARGET: "Python3"
COMPONENT AuthService:
    INTERFACE:
        login() -> Boolean
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    assert isinstance(ast, GASDFile)
    assert len(ast.components) == 1
    assert ast.components[0].name == "AuthService"
    assert len(ast.components[0].methods) == 1
    assert ast.components[0].methods[0].name == "login"

def test_ast_constraints():
    """AT-PARSER-003-03: Constraints link to correct nodes in AST."""
    api = ParseTreeAPI()
    content = """CONTEXT: "ConstraintAST"
TARGET: "Python3"
CONSTRAINT: "Data integrity"
INVARIANT: "Always true"
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    assert len(ast.constraints) == 2
    assert ast.constraints[0].text == "Data integrity"
    assert ast.constraints[1].text == "Always true"
    assert ast.constraints[0].kind == "Constraint"
    assert ast.constraints[1].kind == "Invariant"
