import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.SemanticNodes import ResolvedTypeNode, ResolvedFieldNode, TypeContract, ResolvedExpression, SemanticNodeBase, SourceRange
from Impl.semantic.TypeContractBinder import BinderEngine, BoundTypeContract

def scaffold_binder_and_schema():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    user_fields = {
        "id": ResolvedFieldNode("id", TypeContract("Integer"), False),
        "name": ResolvedFieldNode("name", TypeContract("String"), False),
        "email": ResolvedFieldNode("email", TypeContract("String"), True) # optional
    }
    user_type = ResolvedTypeNode(SourceRange("", 0, 0, 0, 0), "User", user_fields, False)
    
    # Nested struct
    profile_fields = {
        "user": ResolvedFieldNode("user", TypeContract("User"), False),
        "bio": ResolvedFieldNode("bio", TypeContract("String"), False)
    }
    profile_type = ResolvedTypeNode(SourceRange("", 0, 0, 0, 0), "Profile", profile_fields, False)

    table.define(SymbolEntry("User", SymbolKind.Type, table.current_scope, user_type))
    table.define(SymbolEntry("Profile", SymbolKind.Type, table.current_scope, profile_type))
    
    return BinderEngine(table), user_type, profile_type, table


def test_semast_structural_compatibility():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 1, "name": "Alice"})
    contract = engine.bind(expr, "User")
    
    assert contract.isValid is True
    assert "id" in contract.boundProperties
    assert contract.boundProperties["id"].resolvedValue == 1


def test_semast_bind_expression():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 2, "name": "Bob", "email": "bob@example.com"})
    contract = engine.bind(expr, "User")
    
    assert isinstance(contract, BoundTypeContract)
    assert contract.targetType == "User"
    assert contract.isValid is True


def test_semast_verify_fields():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    # Pass subset, MISSING 'name'
    contract = engine.verify_fields({"id": 3}, user_type)
    assert contract.isValid is False
    assert "name" in contract.missingFields


def test_semast_property_propagation():
    engine, user_type, _, table = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 4, "name": "Charlie"})
    contract = engine.bind(expr, "User")
    
    engine.propagate(contract, table.current_scope)
    
    assert table.resolve("id") is not None
    assert table.resolve("name") is not None


def test_semast_binding_engine():
    engine, user_type, _, table = scaffold_binder_and_schema()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 1, "name": "Test"})
    contract = engine.bind(expr, "User")
    assert contract.isValid is True


def test_semast_missing_fields():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"email": "missing_req@example.com"})
    contract = engine.bind(expr, "User")
    
    assert contract.isValid is False
    assert "id" in contract.missingFields
    assert "name" in contract.missingFields


def test_semast_nested_structure():
    engine, user_type, profile_type, _ = scaffold_binder_and_schema()
    
    # user is missing 'name'
    raw_data = {
        "user": {"id": 1},
        "bio": "Hello"
    }
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), raw_data)
    contract = engine.bind(expr, "Profile")
    
    assert contract.isValid is False


def test_semast_lazy_resolution():
    # A generic test to verify depth limits or lazy resolving
    engine, user_type, profile_type, table = scaffold_binder_and_schema()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"user": {"id": 1, "name": "N"}, "bio": "B"})
    contract = engine.bind(expr, "Profile")
    assert contract.isValid is True

def test_semast_binding_regression_optional():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 5, "name": "Dave"})
    contract = engine.bind(expr, "User")
    
    assert contract.isValid is True


def test_semast_binding_regression_extra_fields():
    engine, user_type, _, _ = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 6, "name": "Eve", "age": 30})
    contract = engine.bind(expr, "User")
    
    assert contract.isValid is True
    assert "age" in contract.extraFields
