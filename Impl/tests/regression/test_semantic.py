import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

def test_historical_specs_validity():
    """RT-PARSER-004-01: Valid historical specs remain valid."""
    api = ParseTreeAPI()
    # A standard valid GASD file should always pass
    content = """CONTEXT: "HistoricalValid"
TARGET: "Python3"
TYPE User:
    id: Integer
COMPONENT AuthService:
    INTERFACE:
        login(u: User) -> Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    assert len(semantic_errors) == 0

def test_validation_behavior_stability():
    """RT-PARSER-004-02: Validation logic does not change expected behavior."""
    api = ParseTreeAPI()
    # Known invalid: duplicate names should always produce V001
    content = """CONTEXT: "StableBehavior"
TARGET: "Python3"
TYPE Dup:
    f: String
TYPE Dup:
    g: Integer
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    codes = [e.code for e in semantic_errors]
    assert 'V001' in codes, f"Expected V001 for duplicate names, got: {codes}"
