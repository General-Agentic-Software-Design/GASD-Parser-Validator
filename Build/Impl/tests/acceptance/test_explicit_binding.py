import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Acceptance Test for US-PARSER-008: GEP-5 Explicit VALIDATE AS TYPE Binding
@trace #AT-VALIDATE-001, #AT-VALIDATE-002, #NT-VALIDATE-001, #NT-VALIDATE-002
"""

def test_explicit_binding_syntax_success():
    """AT-VALIDATE-001: Explicit binding 'AS TYPE.Path' is accepted."""
    content = """CONTEXT: "GEP5"
TARGET: "P"
FLOW F():
    1. ACHIEVE "A"
    2. VALIDATE user AS TYPE.User
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

def test_explicit_binding_syntax_failure():
    """NT-VALIDATE-001: Missing 'AS TYPE' binding causes syntax error."""
    content = """CONTEXT: "GEP5"
TARGET: "P"
FLOW F():
    1. VALIDATE user  # Missing AS TYPE
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_complex_type_path_binding():
    """AT-VALIDATE-002: Dot-notation complex paths are accepted."""
    content = """CONTEXT: "GEP5"
TARGET: "P"
FLOW F():
    1. VALIDATE address AS TYPE.User.Address
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

def test_ast_binding_mapping():
    """AC-PARSER-008-04: AST nodes capture binding info."""
    content = """CONTEXT: "GEP5"
TARGET: "P"
FLOW F():
    1. VALIDATE u AS TYPE.User
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    ast = ASTGenerator().visit(tree)
    
    # Check FlowStepNode for binding info
    step = ast.flows[0].steps[0]
    assert step.action == "VALIDATE"
    assert step.asBinding == "AS TYPE"
    assert step.typePath == "User"

def test_binding_resolution_failure():
    """NT-VALIDATE-002: Binding to non-existent Type fails semantic validation."""
    content = """CONTEXT: "GEP5"
TARGET: "P"
FLOW F():
    1. VALIDATE u AS TYPE.UnknownType
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    sem_errors = pipeline.validate(ast)
    
    assert any("UnknownType" in e.message and "resolve" in e.message.lower() for e in sem_errors)
