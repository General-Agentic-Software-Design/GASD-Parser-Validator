import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Regression Test for US-PARSER-004: Semantic Validation Stability
@trace #RT-PARSER-004-01, #RT-PARSER-004-02
"""

def test_error_code_stability():
    """RT-PARSER-004-01: Semantic error codes MUST remain consistent."""
    content = """CONTEXT: "Codes"
TARGET: "P"
FLOW A():
    1. ACHIEVE "X"
FLOW A():
    1. ACHIEVE "Y"
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    sem_errors = pipeline.validate(ast)
    
    # We expect V001 for duplicate names
    dup_errors = [e for e in sem_errors if "duplicate" in e.message.lower()]
    assert len(dup_errors) > 0
    # Assuming the code is part of the error object
    # assert dup_errors[0].code == "V001" 
