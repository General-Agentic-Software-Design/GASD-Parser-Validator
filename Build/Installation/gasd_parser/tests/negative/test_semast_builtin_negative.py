import pytest
from Impl.semantic.SymbolTable import SymbolTable, SemanticError, SymbolEntry, SymbolKind
from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange

def test_builtin_collision_global():
    """
    NT-SEMAST-019-01: Collision attempt in global scope.
    """
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    entry = SymbolEntry("Integer", SymbolKind.Type, table.global_scope, node)
    
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(entry)

def test_builtin_shadowing_rejection_nested():
    """
    Ensure shadowing is rejected even in deeply nested scopes.
    """
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    table.enter_scope("namespace")
    table.enter_scope("method")
    table.enter_scope("block")
    
    entry = SymbolEntry("Boolean", SymbolKind.Variable, table.current_scope, node)
    with pytest.raises(SemanticError, match="Shadowing error"):
        table.define(entry)

def test_resolve_non_existent_builtin():
    """
    Verify that non-existent types still fail resolution.
    """
    table = SymbolTable()
    assert table.resolve("NonExistentType") is None
    
def test_invalid_case_builtin_resolution():
    """
    GASD is case-sensitive. 'string' should not resolve to 'String'.
    """
    table = SymbolTable()
    assert table.resolve("string") is None
    assert table.resolve("int") is None
