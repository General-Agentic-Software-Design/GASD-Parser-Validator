"""
GASD 1.1 Literal Types — Acceptance Tests (GEP-2)
Tests that string, integer, and float literals are valid as type expressions.
"""
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline


# -----------------------------------------------------------------------
# Grammar: Literal types parse without syntax errors
# -----------------------------------------------------------------------

def test_string_literal_type_parses():
    """GASD 1.1 / GEP-2: A string literal used as a field type parses successfully."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralTest"
TARGET: "Python3"
TYPE StatusEvent:
    status: "PENDING"
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Unexpected errors: {errors.to_console()}"


def test_integer_literal_type_parses():
    """GASD 1.1 / GEP-2: An integer literal used as a field type parses successfully."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralTest"
TARGET: "Python3"
TYPE VersionedData:
    version: 1
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Unexpected errors: {errors.to_console()}"


def test_float_literal_type_parses():
    """GASD 1.1 / GEP-2: A float literal used as a field type parses successfully."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralTest"
TARGET: "Python3"
TYPE Config:
    threshold: 0.5
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Unexpected errors: {errors.get_errors()}"


# -----------------------------------------------------------------------
# AST: Literal types populate literalValue and set baseType to "literal"
# -----------------------------------------------------------------------

def test_string_literal_ast_node():
    """GASD 1.1 / GEP-2: String literal type is stored in AST with literalValue populated."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralAST"
TARGET: "Python3"
TYPE Event:
    status: "ACTIVE"
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)

    field = ast.types[0].fields[0]
    assert field.type.baseType == "literal"
    assert field.type.literalValue == '"ACTIVE"'


def test_integer_literal_ast_node():
    """GASD 1.1 / GEP-2: Integer literal type is stored in AST with literalValue populated."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralAST"
TARGET: "Python3"
TYPE Versioned:
    apiVersion: 2
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)

    field = ast.types[0].fields[0]
    assert field.type.baseType == "literal"
    assert field.type.literalValue == "2"


# -----------------------------------------------------------------------
# Semantic Validation: Literal types do NOT trigger V008 (unknown type ref)
# -----------------------------------------------------------------------

def test_literal_type_no_false_positive_v008():
    """GASD 1.1 / GEP-2: Literal string type does not raise V008 unresolved type error."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralValidation"
TARGET: "Python3"
TYPE Order:
    state: "DRAFT"
    code: 42
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)

    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)

    v008_errors = [e for e in semantic_errors if e.code == 'V008']
    assert len(v008_errors) == 0, (
        f"Literal types incorrectly flagged as unknown type references: {v008_errors}"
    )


def test_non_literal_unknown_type_still_caught():
    """Regression: Non-literal unknown identifier type still triggers V008."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "LiteralValidation"
TARGET: "Python3"
COMPONENT MyComp:
    INTERFACE:
        run(u: GhostType) -> Boolean
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)

    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)

    v008_errors = [e for e in semantic_errors if e.code == 'V008']
    assert len(v008_errors) > 0
    assert any("GhostType" in e.message for e in v008_errors)
