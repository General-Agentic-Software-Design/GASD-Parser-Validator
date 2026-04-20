"""
Negative Tests: Enforce INVARIANT Scope Ordering (US-PARSER-012)
==================================================================
Validates that 'GLOBAL INVARIANT' and 'LOCAL INVARIANT' are rejected.
Trace: US-PARSER-012
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

@pytest.fixture
def api():
    return ParseTreeAPI()

def test_global_invariant_ordering_rejected(api):
    """AC-PARSER-012-02: 'GLOBAL INVARIANT:' must be rejected."""
    content = 'VERSION 1.2\nGLOBAL INVARIANT: "Invalid order"\n'
    tree, reporter = api.parse(content)
    # This is expected to FAIL until implementation in Phase 4
    assert reporter.get_error_count() > 0, "Invalid 'GLOBAL INVARIANT' should be rejected"

def test_local_invariant_ordering_rejected(api):
    """AC-PARSER-012-02: 'LOCAL INVARIANT:' must be rejected."""
    content = 'VERSION 1.2\nLOCAL INVARIANT: "Invalid order"\n'
    tree, reporter = api.parse(content)
    # This is expected to FAIL until implementation in Phase 4
    assert reporter.get_error_count() > 0, "Invalid 'LOCAL INVARIANT' should be rejected"

def test_error_message_hint(api):
    """AC-PARSER-012-03: Error message should suggest correct order."""
    content = 'VERSION 1.2\nGLOBAL INVARIANT: "Invalid order"\n'
    tree, reporter = api.parse(content)
    if reporter.get_error_count() > 0:
        error = reporter.syntax_errors[0]
        assert "INVARIANT GLOBAL" in error.message or "INVARIANT LOCAL" in error.message
