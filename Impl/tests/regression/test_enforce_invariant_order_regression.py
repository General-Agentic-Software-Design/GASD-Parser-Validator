"""
Regression Tests: Enforce INVARIANT Scope Ordering (US-PARSER-012)
===================================================================
Ensures existing valid invariant uses remain unaffected.
Trace: US-PARSER-012
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

@pytest.fixture
def api():
    return ParseTreeAPI()

def test_unscoped_invariant_regression(api):
    """RT-PARSER-012-01: Unscoped INVARIANT (valid in 1.1) should not trigger syntax error."""
    content = 'VERSION 1.1\nINVARIANT: "General property"\n'
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0

def test_existing_example_regression(api):
    """RT-PARSER-012-01: Existing correctly ordered examples must continue to pass."""
    content = (
        'VERSION 1.2\n'
        'INVARIANT GLOBAL: "Average(PowerNode.frequency_hz) >= 49.5"\n'
    )
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0
