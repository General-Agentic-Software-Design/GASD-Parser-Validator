"""
GASD 1.1 Literal Types — Regression Tests (GEP-2)
Ensures adding literal type support does not break pre-existing identifier-based types.
"""
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline


def test_identifier_type_backward_compat():
    """RT: Identifier-based type fields still parse and produce correct AST after GASD 1.1 changes."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "BackCompat"
TARGET: "Python3"
TYPE Order:
    id: Integer
    name: String
    active: Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

    generator = ASTGenerator()
    ast = generator.visit(tree)

    fields = {f.name: f.type for f in ast.types[0].fields}
    # Identifier types should have no literalValue
    assert fields["id"].literalValue is None
    assert fields["id"].baseType == "Integer"
    assert fields["name"].literalValue is None
    assert fields["name"].baseType == "String"


def test_literal_and_identifier_types_coexist():
    """RT: A TYPE with mixed literal and identifier fields is valid and correct in AST."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "MixedTypes"
TARGET: "Python3"
TYPE Order:
    status: "PENDING"
    priority: Integer
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

    generator = ASTGenerator()
    ast = generator.visit(tree)

    fields = {f.name: f.type for f in ast.types[0].fields}

    # Literal field
    assert fields["status"].baseType == "literal"
    assert fields["status"].literalValue == '"PENDING"'

    # Identifier field — unchanged behavior
    assert fields["priority"].baseType == "Integer"
    assert fields["priority"].literalValue is None


def test_generic_types_unaffected():
    """RT: Generic types (List, Optional, Map) still work correctly after GASD 1.1 changes."""
    api = ParseTreeAPI()
    content = """\
CONTEXT: "Generics"
TARGET: "Python3"
TYPE Container:
    tags: List<String>
    meta: Optional<Integer>
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0

    generator = ASTGenerator()
    ast = generator.visit(tree)

    fields = {f.name: f.type for f in ast.types[0].fields}
    assert fields["tags"].baseType == "List"
    assert fields["tags"].literalValue is None
    assert fields["meta"].isOptional is True
    assert fields["meta"].literalValue is None
