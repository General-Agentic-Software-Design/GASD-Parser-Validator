import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_grammar_permissive_tokens():
    """Validates §8: Permissive natural language in ACHIEVE/ENSURE."""
    content = """CONTEXT: "Test"
TARGET: "T"
FLOW F():
  1. ACHIEVE "Everything is awesome!"
  2. ENSURE "The system works as intended"
"""
    api = ParseTreeAPI()
    tree, reporter = api.parse(content)
    assert not reporter.has_errors()

def test_grammar_indented_blocks():
    """Validates §5: Indentation-based scoping."""
    content = """CONTEXT: "Test"
TYPE T:
  f1: String
  f2: Integer
"""
    api = ParseTreeAPI()
    tree, reporter = api.parse(content)
    assert not reporter.has_errors()
