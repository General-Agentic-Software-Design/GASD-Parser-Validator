import pytest
import json
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.errors.ErrorReporter import ErrorReporter

"""
Acceptance Test for US-PARSER-005: Error Reporting System
@trace #AT-PARSER-005-01, #AC-PARSER-005-03
"""

def test_syntax_error_reporting():
    """AT-PARSER-005-01: Syntax errors must show location and context."""
    content = 'CONTEXT "MissingColon"\n' # Syntax error: missing colon
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    
    console_output = errors.to_console()
    assert "1:8" in console_output # Line 1, approx column 8
    assert "MissingColon" in console_output
    assert "^" in console_output # Location indicator

def test_json_error_reporting():
    """AC-PARSER-005-03: Machine-readable JSON output."""
    content = 'CONTEXT "MissingColon"\n'
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    
    json_report = errors.to_json()
    report_data = json.loads(json_report)
    
    assert report_data["success"] is False
    assert report_data["errorCount"] > 0
    assert "errors" in report_data
    assert report_data["errors"][0]["type"] == "SYNTAX"
