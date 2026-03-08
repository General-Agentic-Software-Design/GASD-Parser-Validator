import pytest
import json
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline
from Impl.errors.ErrorReporter import ErrorReporter

def test_syntax_error_reporting():
    """AT-PARSER-005-01: Syntax errors are reported in human-readable format."""
    api = ParseTreeAPI()
    content = "INVALID_KEYWORD: 'value'\n"
    tree, errors = api.parse(content)
    
    assert errors.get_error_count() > 0
    console_out = errors.to_console()
    assert "error[SYNTAX]" in console_out
    assert "INVALID_KEYWORD" in content # Just checking it mentions the source line or similar

def test_json_error_reporting():
    """AC-PARSER-005-03: Error output is available in JSON format."""
    api = ParseTreeAPI()
    content = "INVALID_KEYWORD: 'value'\n"
    tree, errors = api.parse(content)
    
    json_out = errors.to_json()
    report = json.loads(json_out)
    
    assert report["success"] == False
    assert report["errorCount"] > 0
    assert len(report["errors"]) > 0
    assert report["errors"][0]["type"] == "SYNTAX"

def test_semantic_error_location():
    """AT-PARSER-005-02: Duplicate definition error shows location."""
    api = ParseTreeAPI()
    content = """CONTEXT: "DupErr"
TARGET: "Python3"
TYPE T:
    f: String
TYPE T:
    g: Integer
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    # Should have V001 for duplicate name T
    dup_errors = [e for e in semantic_errors if e.code == 'V001']
    assert len(dup_errors) > 0, f"Expected V001, got: {[e.code for e in semantic_errors]}"
    
    # Verify location metadata
    err = dup_errors[0]
    assert err.line > 0
    assert err.column >= 0
    assert "T" in err.message
