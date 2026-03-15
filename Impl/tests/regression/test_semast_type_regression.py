import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind
from Impl.semantic.SemanticNodes import ResolvedTypeNode, ResolvedFieldNode, TypeContract, ResolvedExpression, SemanticNodeBase, SourceRange
from Impl.semantic.TypeContractBinder import BinderEngine, BoundTypeContract

def scaffold():
    table = SymbolTable()
    fields = {
        "id": ResolvedFieldNode("id", TypeContract("Integer"), False),
        "name": ResolvedFieldNode("name", TypeContract("String"), False),
        "email": ResolvedFieldNode("email", TypeContract("String"), True)
    }
    user_type = ResolvedTypeNode(SourceRange("", 0, 0, 0, 0), "User", fields, False)
    
    profile_fields = {
        "user": ResolvedFieldNode("user", TypeContract("User"), False),
        "bio": ResolvedFieldNode("bio", TypeContract("String"), False)
    }
    profile_type = ResolvedTypeNode(SourceRange("", 0, 0, 0, 0), "Profile", profile_fields, False)
    
    table.define(SymbolEntry("User", SymbolKind.Type, table.current_scope, user_type))
    table.define(SymbolEntry("Profile", SymbolKind.Type, table.current_scope, profile_type))
    return BinderEngine(table), user_type, profile_type, table

def test_semast_structural_compatibility():
    engine, _, _, _ = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 1, "name": "Alice"})
    contract = engine.bind(expr, "User")
    assert contract.isValid is True

def test_semast_bind_expression():
    engine, _, _, _ = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 2, "name": "Bob", "email": "b@x.com"})
    contract = engine.bind(expr, "User")
    assert isinstance(contract, BoundTypeContract)
    assert contract.targetType == "User"

def test_semast_verify_fields():
    engine, user_type, _, _ = scaffold()
    contract = engine.verify_fields({"id": 3}, user_type)
    assert contract.isValid is False
    assert "name" in contract.missingFields

def test_semast_property_propagation():
    engine, _, _, table = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 4, "name": "Charlie"})
    contract = engine.bind(expr, "User")
    engine.propagate(contract, table.current_scope)
    assert table.resolve("id") is not None

def test_semast_binding_engine():
    engine, _, _, table = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 1, "name": "Test"})
    contract = engine.bind(expr, "User")
    assert contract.isValid is True

def test_semast_missing_fields():
    engine, _, _, _ = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"email": "m@x.com"})
    contract = engine.bind(expr, "User")
    assert contract.isValid is False
    assert "id" in contract.missingFields

def test_semast_nested_structure():
    engine, _, _, _ = scaffold()
    raw = {"user": {"id": 1}, "bio": "Hello"}
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), raw)
    contract = engine.bind(expr, "Profile")
    assert contract.isValid is False

def test_semast_lazy_resolution():
    engine, _, _, table = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"user": {"id": 1, "name": "N"}, "bio": "B"})
    contract = engine.bind(expr, "Profile")
    assert contract.isValid is True

def test_semast_binding_regression_optional():
    engine, _, _, _ = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 5, "name": "Dave"})
    contract = engine.bind(expr, "User")
    assert contract.isValid is True

def test_semast_binding_regression_extra_fields():
    engine, _, _, _ = scaffold()
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {"id": 6, "name": "Eve", "age": 30})
    contract = engine.bind(expr, "User")
    assert contract.isValid is True
    assert "age" in contract.extraFields
