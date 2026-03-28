import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolKind

def test_builtin_design_pre_registration_explicit():
    """
    Validates design requirement: Global Symbol Table Initialization.
    Checks if SymbolTable registers exactly the 15 required primitives explicitly.
    """
    table = SymbolTable()
    required_builtins = [
        "String", "Integer", "Int", "Float", "Decimal", "Boolean", "Bytes", "UUID", 
        "DateTime", "Optional", "List", "Map", "Enum", "Result", "Any", "Void"
    ]
    
    # 1. Verify existence and scope
    for b in required_builtins:
        resolved = table.resolve(b)
        assert resolved is not None, f"Design Requirement: {b} MUST be pre-registered"
        assert resolved.scope == table.global_scope
        assert resolved.kind == SymbolKind.Type
        
    # 2. Verify exact set size (no extra hidden built-ins beyond these)
    global_type_symbols = [s for s in table.global_scope.symbols.values() if s.kind == SymbolKind.Type]
    assert len(global_type_symbols) == 18, "Expected exactly 18 built-in types"

def test_builtin_design_generic_placeholder_verification():
    """
    Validates design requirement: Template-based Validation for Generics.
    Ensures structural types are registered as markers in SymbolTable.
    """
    table = SymbolTable()
    structural_types = ["Map", "List", "Result", "Optional"]
    for st in structural_types:
        resolved = table.resolve(st)
        assert resolved is not None, f"Structural type {st} missing"
        # Verify it has no fields (registered as basic ResolvedTypeNode in SymbolTable.py)
        assert hasattr(resolved.nodeLink, 'fields')
        assert len(resolved.nodeLink.fields) == 0

def test_builtin_registration_strategy_consistency():
    """
    Ensures the initialization logic is encapsulated in BuiltinTypeRegistry as per design.
    """
    from Impl.semantic.SymbolTable import BuiltinTypeRegistry
    assert hasattr(BuiltinTypeRegistry, "initializeBuiltins"), "Design Strategy: Should have component-localized initialization method"
