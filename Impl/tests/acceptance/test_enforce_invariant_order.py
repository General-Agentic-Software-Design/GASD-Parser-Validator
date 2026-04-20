"""
Acceptance Tests: Enforce INVARIANT Scope Ordering (US-PARSER-012)
==================================================================
Validates that 'INVARIANT GLOBAL' and 'INVARIANT LOCAL' patterns are
correctly accepted by the parser.
Trace: US-PARSER-012
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

@pytest.fixture
def api():
    return ParseTreeAPI()

def test_invariant_global_ordering_accepted(api):
    """AC-PARSER-012-01: 'INVARIANT GLOBAL:' must be accepted."""
    content = 'VERSION 1.2\nINVARIANT GLOBAL: "System must be stable"\n'
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0, f"Valid 'INVARIANT GLOBAL' should be accepted. Errors: {reporter.to_console()}"

def test_invariant_local_ordering_accepted(api):
    """AC-PARSER-012-01: 'INVARIANT LOCAL:' must be accepted."""
    content = 'VERSION 1.2\nINVARIANT LOCAL: "Component property"\n'
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0, f"Valid 'INVARIANT LOCAL' should be accepted. Errors: {reporter.to_console()}"

def test_invariant_with_id_ordering_accepted(api):
    """AC-PARSER-012-01: Scoped invariant with identifier must be accepted."""
    content = 'VERSION 1.2\nINVARIANT GLOBAL StabilityRule: "Stable"\n'
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0
