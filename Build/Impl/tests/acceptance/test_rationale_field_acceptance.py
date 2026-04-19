"""
Acceptance Tests: Rationale Field Mandatory (BUG-2)
====================================================
Validates that a DECISION block with RATIONALE present compiles correctly
and produces the expected AST structure.
Based on Validation/Acceptance/rationale_field_acceptance.gasd
Trace: BUG-2
"""

import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator


@pytest.fixture
def api():
    return ParseTreeAPI()


def test_decision_with_rationale_parses_successfully(api):
    """BUG-2 Acceptance: DECISION with RATIONALE must parse without errors."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Error Strategy":\n'
        '    CHOSEN: "Exception-based"\n'
        '    RATIONALE: "Industry standard approach"\n'
        '    ALTERNATIVES: ["Error codes", "Result monad"]\n'
        '    AFFECTS: [*]\n'
    )
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0, "Valid DECISION with RATIONALE should parse without errors"


def test_decision_ast_rationale_populated(api):
    """BUG-2 Acceptance: Decision AST node must have rationale as a non-empty string."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "Password Storage":\n'
        '    CHOSEN: "bcrypt"\n'
        '    RATIONALE: "Industry standard, available in all target languages"\n'
        '    AFFECTS: [User.password_hash]\n'
    )
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0
    ast = ASTGenerator().visit(tree)
    assert len(ast.decisions) == 1
    decision = ast.decisions[0]
    assert decision.rationale is not None
    assert decision.rationale != ""
    assert decision.rationale == "Industry standard, available in all target languages"


def test_decision_ast_retains_all_fields_with_rationale(api):
    """BUG-2 Acceptance: Decision AST node retains chosen, alternatives, and affects alongside rationale."""
    content = (
        'CONTEXT: "C"\n'
        'TARGET: "P"\n'
        'DECISION "DB Choice":\n'
        '    CHOSEN: "PostgreSQL"\n'
        '    RATIONALE: "Strong ACID compliance"\n'
        '    ALTERNATIVES: ["MySQL", "MongoDB"]\n'
        '    AFFECTS: [UserService, OrderService]\n'
    )
    tree, reporter = api.parse(content)
    assert reporter.get_error_count() == 0
    ast = ASTGenerator().visit(tree)
    assert len(ast.decisions) == 1
    decision = ast.decisions[0]
    assert decision.chosen == "PostgreSQL"
    assert decision.rationale == "Strong ACID compliance"
    assert decision.alternatives is not None
    assert len(decision.alternatives) == 2
    assert decision.affects is not None
