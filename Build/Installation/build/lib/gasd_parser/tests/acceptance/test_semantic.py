import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Acceptance Test for US-PARSER-004: Semantic Validation Engine
@trace #AT-PARSER-004-01, #AT-PARSER-004-02, #AT-PARSER-004-03
"""

def test_duplicate_name_detection():
    """AT-PARSER-004-01: No duplicate construct names allowed."""
    content = """CONTEXT: "DuplicateTest"
TARGET: "Python3"
FLOW Auth():
    1. ACHIEVE "A"
FLOW Auth():
    1. ACHIEVE "B"
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    # The parser might allow duplicates, but the validator must catch them
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    sem_errors = pipeline.validate(ast)
    
    # Check for duplicate FLOW name error
    has_dup_error = any("duplicate" in e.message.lower() and "Auth" in e.message for e in sem_errors)
    assert has_dup_error, "Failed to detect duplicate FLOW names"

def test_required_sections_present():
    """AT-PARSER-004-02: Mandatory sections must exist."""
    content = """TARGET: "Python3"
# Missing CONTEXT
TYPE T: f: String
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    sem_errors = pipeline.validate(ast)
    
    # Check for missing CONTEXT directive
    has_context_error = any("CONTEXT" in e.message for e in sem_errors)
    assert has_context_error, "Failed to detect missing CONTEXT directive"

def test_reference_resolution():
    """AT-PARSER-004-03: References must resolve."""
    content = """CONTEXT: "RefTest"
TARGET: "Python3"
FLOW Main():
    1. VALIDATE user AS TYPE.MissingType
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    sem_errors = pipeline.validate(ast)
    
    # Check for unresolved type reference
    has_ref_error = any("MissingType" in e.message and "resolve" in e.message.lower() for e in sem_errors)
    assert has_ref_error, "Failed to detect unresolved TYPE reference"
