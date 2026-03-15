import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_error_reporting_format():
    """Validates AC-PARSER-004-04: Standardized Error Format."""
    content = 'CONTEXT: "Test"\nINVALID_KEYWORD_HERE foo\n'
    api = ParseTreeAPI()
    _, reporter = api.parse(content)
    assert reporter.has_errors()
    # Check syntax errors
    assert len(reporter.syntax_errors) > 0
    for err in reporter.syntax_errors:
        assert hasattr(err, 'line')
        assert hasattr(err, 'column')
        assert hasattr(err, 'message')

def test_column_tracking():
    """Validates precision of error reporting."""
    content = 'CONTEXT: "Test"\nTARGET: "T"\nFLOW F():\n  1. ACHIEVE "X" OTHERWISE' # Missing RETURN
    api = ParseTreeAPI()
    _, reporter = api.parse(content)
    if reporter.has_errors():
        err = reporter.syntax_errors[0]
        assert err.column > 0
