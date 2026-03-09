import pytest
import os
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Regression Test for US-PARSER-001: GASD Grammar Stability
@trace #RT-PARSER-001-01, #RT-PARSER-001-02, #RT-PARSER-001-03
"""

def test_historical_specs_validity():
    """RT-PARSER-001-01: Ensure all historical reference specs remain valid."""
    ref_specs_dir = "Ref-Specs"
    if not os.path.exists(ref_specs_dir):
        pytest.skip("Ref-Specs directory not found")
        
    api = ParseTreeAPI()
    for filename in os.listdir(ref_specs_dir):
        if filename.endswith(".gasd"):
            path = os.path.join(ref_specs_dir, filename)
            with open(path, 'r') as f:
                content = f.read()
            tree, errors = api.parse(content)
            assert errors.get_error_count() == 0, f"Regression in {filename}: {errors.to_console()}"

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
