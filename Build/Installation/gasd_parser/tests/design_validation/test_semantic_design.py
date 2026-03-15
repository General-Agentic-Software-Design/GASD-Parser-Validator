import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Design Validation: Semantic Validation
Mapped from Validation/semantic_validation_tests.gasd
"""

def test_design_duplicate_names():
    """FLOW test_duplicate_names"""
    content = 'CONTEXT: "D"\nTARGET: "P"\nTYPE T: f: S\nTYPE T: f: S\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("duplicate" in e.message.lower() for e in errors)

def test_design_required_sections():
    """FLOW test_required_sections"""
    content = 'TARGET: "P"\n' # Missing CONTEXT
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("CONTEXT" in e.message for e in errors)

def test_design_validate_as_type_resolution():
    """FLOW test_validate_as_type_resolution (GEP-5)"""
    content = 'CONTEXT: "G"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE u AS TYPE.Unknown\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("Unknown" in e.message and "resolve" in e.message.lower() for e in errors)
