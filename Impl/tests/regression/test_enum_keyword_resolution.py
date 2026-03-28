import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_enum_keywords_resolution():
    """
    Regression Test: Ensures that flow keywords (like VALIDATE, ACHIEVE, OTHERWISE)
    can be used natively inside an Enum declaration as parameter values without causing
    syntax errors (specifically testing keyword -> soft_id fallback).
    """
    source = '''
CONTEXT: "Test Enum Keywords inside Type"
TARGET: "TypeScript"
NAMESPACE: "Test"

TYPE StepConfig:
    action: Enum(VALIDATE, ACHIEVE, CREATE, PERSIST, RETURN, LOG, EXECUTE, TRANSFORM, ENSURE, MATCH, IF, ELSE, APPLY, UPDATE, ON_ERROR, OTHERWISE, THROW)
    '''
    # Parsing should succeed without syntax errors
    api = ParseTreeAPI()
    tree, reporter = api.parse(source)
    assert tree is not None
    assert not reporter.has_errors(), f"Expected no errors, but found: {reporter.syntax_errors}"
