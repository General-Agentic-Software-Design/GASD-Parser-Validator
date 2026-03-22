import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind
from Impl.semantic.SemanticNodes import SourceRange, SemanticNodeBase

def test_semast_symbol_definition_and_lookup():
    """Validates core symbol registration and retrieval."""
    table = SymbolTable()
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    node = SemanticNodeBase("Type", sr)
    entry = SymbolEntry("MyType", SymbolKind.Type, table.current_scope, node)
    table.define(entry)
    
    symbol = table.resolve("MyType")
    assert symbol is not None
    assert symbol.kind == SymbolKind.Type

def test_semast_scope_hierarchy_isolation():
    """Validates that scopes provide proper isolation."""
    table = SymbolTable()
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    node = SemanticNodeBase("Var", sr)
    
    table.enter_scope("Namespace1")
    entry = SymbolEntry("LocalSym", SymbolKind.Variable, table.current_scope, node)
    table.define(entry)
    assert table.resolve("LocalSym") is not None
    
    table.exit_scope()
    assert table.resolve("LocalSym") is None

def test_semast_recursion_check_requirement():
    """Validates requirement for recursion checking."""
    from Impl.semantic.SymbolTable import SymbolTable
    table = SymbolTable()
    assert hasattr(table, "check_recursion")

# ===================================================================
# Cross-File Design Validation
# ===================================================================

def test_semast_cross_file_symbol_visibility():
    """Validates AC-X-SEMAST-003-01: Cross-file symbol visibility in global scope."""
    table = SymbolTable()
    # Symbol in global scope should be visible to other files
    sr = SourceRange("file-b.gasd", 1, 0, 1, 1)
    node = SemanticNodeBase("Type", sr)
    table.define(SymbolEntry("SharedType", SymbolKind.Type, table.global_scope, node))
    
    assert table.resolve("SharedType") is not None

def test_semast_cross_file_symbol_collision():
    """Validates AC-X-SEMAST-003-02: Collision detection for identically named symbols in same namespace."""
    table = SymbolTable()
    table.define(SymbolEntry("User", SymbolKind.Type, table.global_scope, make_node()))
    
    from Impl.semantic.SymbolTable import SemanticError
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(SymbolEntry("User", SymbolKind.Type, table.global_scope, make_node()))

def test_semast_cross_file_builtin_shadowing():
    """Validates AC-X-SEMAST-003-03: Prevention of shadowing built-in types."""
    table = SymbolTable()
    from Impl.semantic.SymbolTable import SemanticError
    with pytest.raises(SemanticError, match="Collision error|Shadowing error"):
        table.define(SymbolEntry("String", SymbolKind.Type, table.global_scope, make_node()))

def make_node():
    return SemanticNodeBase("Test", SourceRange("", 0,0,0,0))
