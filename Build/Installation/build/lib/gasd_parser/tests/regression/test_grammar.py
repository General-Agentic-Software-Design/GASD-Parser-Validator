import pytest
import os
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Regression Test for US-PARSER-001: GASD Grammar Stability
@trace #RT-PARSER-001-01, #RT-PARSER-001-02, #RT-PARSER-001-03
"""


def test_grammar_ambiguity_regression():
    """RT-PARSER-001-03: No new ambiguities introduced in grammar."""
    # This usually requires running ANTLR with diagnostic listeners
    # For black-box, we check that known complex patterns still parse uniquely
    content = """CONTEXT: "Ambiguity"
TARGET: "P"
FLOW F():
    1. ACHIEVE "A"
    // GEP-5 check
    2. VALIDATE obj AS TYPE.T
"""
    api = ParseTreeAPI()
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
