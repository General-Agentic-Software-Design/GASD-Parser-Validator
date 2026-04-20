"""
Negative Tests: Rationale Field Mandatory (BUG-2)
==================================================
Validates that the parser correctly rejects DECISION blocks
with missing or malformed RATIONALE fields.
Based on Validation/Negative/rationale_field_negative.gasd
Trace: BUG-2
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI


@pytest.fixture
def api():
    return ParseTreeAPI()


def test_decision_no_rationale_rejected(api):
    """BUG-2 Negative: DECISION with CHOSEN but no RATIONALE must be rejected."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Error Strategy":\n'
        '    CHOSEN: "Exception-based"\n'
        '    AFFECTS: [*]\n'
    )
    _, reporter = api.parse(content)
    assert reporter.get_error_count() > 0, \
        "DECISION without RATIONALE must produce a syntax error"


def test_decision_rationale_before_chosen_rejected(api):
    """BUG-2 Negative: DECISION with RATIONALE placed before CHOSEN must be rejected."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Error Strategy":\n'
        '    RATIONALE: "Some reason"\n'
        '    CHOSEN: "Exception-based"\n'
        '    AFFECTS: [*]\n'
    )
    _, reporter = api.parse(content)
    assert reporter.get_error_count() > 0, \
        "DECISION with RATIONALE before CHOSEN must produce a syntax error"
