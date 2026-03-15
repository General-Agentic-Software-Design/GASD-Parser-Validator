import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

def test_semast_validation_duplicate_names():
    """Validates AC-PARSER-004-01: Duplicate Name Detection."""
    content = 'CONTEXT: "D"\nTARGET: "P"\nTYPE T: f: S\nTYPE T: f: S\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("duplicate" in e.message.lower() for e in errors)

def test_semast_validation_required_sections():
    """Validates AC-PARSER-004-02: Required Sections Validation."""
    content = 'TARGET: "P"\n' # Missing CONTEXT
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("CONTEXT" in e.message for e in errors)

def test_semast_validation_reference_resolution():
    """Validates AC-PARSER-004-03: Reference Resolution."""
    content = 'CONTEXT: "G"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE u AS TYPE.Unknown\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    assert any("Unknown" in e.message and "resolve" in e.message.lower() for e in errors)

def test_semast_validation_error_locations():
    """Validates AC-PARSER-004-04: Location Metadata Enrichment."""
    content = 'CONTEXT: "D"\nTARGET: "P"\nTYPE T: f: S\nTYPE T: f: S\n'
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = ValidationPipeline()
    errors = pipeline.validate(ast)
    for err in errors:
        assert err.line > 0
        assert err.column >= 0
        assert err.message != ""
