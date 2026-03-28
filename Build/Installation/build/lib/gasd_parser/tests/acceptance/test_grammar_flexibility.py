"""
Acceptance tests for Grammar Flexibility (Keywords as Identifiers).
Verifies that keywords can be used as field names and Enum values.
"""
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_keywords_as_field_names():
    """Verifies that keywords like CONTEXT and VALIDATE can be used as field names."""
    api = ParseTreeAPI()
    content = """CONTEXT: "KeywordFields"
TARGET: "Python3"
TYPE Node:
    CONTEXT: String
    VALIDATE: Boolean
    TYPE: Integer
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Errors: {errors.to_console()}"
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    fields = {f.name: f.type.baseType for f in ast.types[0].fields}
    assert "CONTEXT" in fields
    assert "VALIDATE" in fields
    assert "TYPE" in fields

def test_keywords_as_enum_values():
    """Verifies that keywords can be used as values within an Enum."""
    api = ParseTreeAPI()
    content = """CONTEXT: "KeywordEnums"
TARGET: "Python3"
TYPE ActionNode:
    actionType: Enum(VALIDATE, ACHIEVE, CONTEXT, TARGET, FLOW)
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Errors: {errors.to_console()}"
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    enum_values = ast.types[0].fields[0].type.enumValues
    assert "VALIDATE" in enum_values
    assert "ACHIEVE" in enum_values
    assert "CONTEXT" in enum_values
    assert "TARGET" in enum_values
    assert "FLOW" in enum_values

def test_complex_mixed_keywords():
    """Verifies a more complex scenario with mixed keywords as IDs."""
    api = ParseTreeAPI()
    content = """CONTEXT: "ComplexKeywords"
TARGET: "Python3"
COMPONENT VALIDATE:
    INTERFACE:
        ACHIEVE(CONTEXT: FLOW) -> TARGET
"""
    # This checks if COMPONENT name (VALIDATE), Method name (ACHIEVE), 
    # Param name (CONTEXT), and Param Type (FLOW) can all be keywords.
    # Note: Currently only field names and enum values are explicitly updated in grammar.
    # If this fails, it's a gap in the grammar for other IDENTIFIER locations.
    tree, errors = api.parse(content)
    # We expect these to fail if COMPONENT/INTERFACE don't use soft_id.
    # But as a test, we should define what the EXPECTED behavior is (it SHOULD work).
    assert errors.get_error_count() == 0, f"Grammar lacks soft_id for components: {errors.to_console()}"

def test_field_names_keyword_collision():
    """Verifies that field names which are keywords parse correctly."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Collision"
TARGET: "Python3"
TYPE FlowStep:
    action: Enum(IF, ELSE, TRANSFORM)
    target: String
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
