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

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_cross_file_qualified_type():
    # AT-X-SEMAST-004-01, AC-X-SEMAST-004-01, AC-X-SEMAST-004-02
    engine, _, _, table = scaffold_binder_and_schema()
    
    # Define "Namespace.Type"
    ns_type = ResolvedTypeNode(SourceRange("remote.gasd", 1, 0, 1, 10), "RemoteType", {}, False)
    table.define(SymbolEntry("Namespace.RemoteType", SymbolKind.Type, table.global_scope, ns_type))
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {})
    # ENSURE "Bind expression against 'Namespace.Type' defined in another file"
    contract = engine.bind(expr, "Namespace.RemoteType")
    
    assert contract.isValid is True
    assert contract.targetType == "Namespace.RemoteType"

def test_semast_cross_file_generic_args():
    # AT-X-SEMAST-007-01, AC-X-SEMAST-004-05
    engine, _, _, table = scaffold_binder_and_schema()
    
    # List is already a builtin, no need to re-define
    # ENSURE "Use a generic type 'List<T>' where T is defined in a different file"
    # User is defined in local scope but T could be anything. 
    # Binder should resolve 'User' during binding 'List<User>'
    expr = ResolvedExpression("List", TypeContract("List", args=[TypeContract("User")]), [])
    contract = engine.bind(expr, "List<User>")
    
    assert contract.isValid is True

def test_semast_missing_cross_file_type():
    # AT-X-SEMAST-004-02, AC-X-SEMAST-004-04
    engine, _, _, table = scaffold_binder_and_schema()
    
    expr = ResolvedExpression("Dict", TypeContract("Dictionary"), {})
    # ENSURE "Reference a non-existent type 'Remote.MissingType'"
    with pytest.raises(SemanticError, match="Unknown type reference"):
        engine.bind(expr, "Remote.MissingType")
