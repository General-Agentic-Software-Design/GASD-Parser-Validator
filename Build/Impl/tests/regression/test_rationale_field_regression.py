"""
Regression Tests: Rationale Field Mandatory (BUG-2)
====================================================
Ensures DECISION blocks without RATIONALE are permanently rejected,
preventing re-introduction of BUG-2.
Based on Validation/Regression/rationale_field_regression.gasd
Trace: BUG-2
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator


@pytest.fixture
def api():
    return ParseTreeAPI()


def test_decision_missing_rationale_raises_syntax_error(api):
    """BUG-2 Regression: DECISION without RATIONALE must be rejected by the parser."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Error Strategy":\n'
        '    CHOSEN: "Exception-based"\n'
        '    ALTERNATIVES: ["Error codes", "Result monad"]\n'
        '    AFFECTS: [*]\n'
    )
    tree, reporter = api.parse(content)
    # After BUG-2 fix, the parser grammar requires RATIONALE.
    # Missing RATIONALE should produce a syntax error.
    assert reporter.get_error_count() > 0, \
        "BUG-2 Regression: DECISION without RATIONALE must produce a syntax error"


def test_decision_with_rationale_still_parses(api):
    """BUG-2 Regression: Valid DECISION blocks with RATIONALE must not be falsely rejected."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Cache Strategy":\n'
        '    CHOSEN: "Redis"\n'
        '    RATIONALE: "Low-latency in-memory store"\n'
        '    ALTERNATIVES: ["Memcached", "Hazelcast"]\n'
        '    AFFECTS: [SessionService]\n'
    )
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0, \
        "BUG-2 Regression: Valid DECISION with RATIONALE must parse without errors"
    ast = ASTGenerator().visit(tree)
    assert len(ast.decisions) == 1
    assert ast.decisions[0].rationale == "Low-latency in-memory store"
