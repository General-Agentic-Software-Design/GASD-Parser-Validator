import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

def test_semantic_duplicate_names():
    """AT-PARSER-004-01: Duplicate names are detected."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Dup"
TARGET: "Python3"
TYPE T1:
    f: String
TYPE T1:
    f: Integer
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    # Filter for the specific V001 (Duplicate) error
    dup_errors = [e for e in semantic_errors if e.code == 'V001']
    assert len(dup_errors) > 0
    assert "Duplicate Type name: 'T1'" in dup_errors[0].message

def test_semantic_missing_required_sections():
    """AT-PARSER-004-02: Missing required sections are detected."""
    api = ParseTreeAPI()
    content = """TRACE: "Missing-Body"
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    codes = [e.code for e in semantic_errors]
    # CONTEXT/TARGET checks are disabled for informal Ref-Specs,
    # but V004 (Empty File Check) MUST trigger if no components exist
    assert 'V004' in codes

def test_semantic_reference_resolution():
    """AT-PARSER-004-03: Unknown reference fails validation."""
    api = ParseTreeAPI()
    content = """CONTEXT: "RefTest"
TARGET: "Python3"
COMPONENT MyComp:
    DEPENDENCIES: ["MissingComp"]
    INTERFACE:
        run(u: UnknownType) -> Boolean
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    codes = [e.code for e in semantic_errors]
    # V009: Unresolved component dependency, V008: Unresolved type
    assert 'V009' in codes
    assert 'V008' in codes
    
    # Verify location metadata for one of the errors
    err = [e for e in semantic_errors if e.code == 'V009'][0]
    assert err.line == 3
    assert "MissingComp" in err.message
