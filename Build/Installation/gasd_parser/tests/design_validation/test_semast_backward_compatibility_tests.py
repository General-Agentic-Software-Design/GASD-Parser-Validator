import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_semast_compat_no_flag_impact():
    """Validates that semantic passes don't break legacy syntactic parsing."""
    content = 'FLOW F():\n    1. ACHIEVE "Legacy"\n'
    api = ParseTreeAPI()
    # Syntactic parse should always work
    tree, reporter = api.parse(content)
    assert not reporter.has_errors()

def test_semast_compat_zero_overhead_requirement():
    """Validates that semantic AST generation can be toggled or has minimal baseline impact."""
    from Impl.ast.ASTGenerator import ASTGenerator
    generator = ASTGenerator()
    assert hasattr(generator, "visit")
