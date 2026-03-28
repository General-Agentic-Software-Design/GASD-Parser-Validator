import pytest
from Impl.semantic.SymbolTable import SymbolTable

def test_legacy_builtin_types_persistence():
    """
    US-SEMAST-020: Ensure previously supported built-in types (String, Integer, etc.) 
    remain functional and correctly registered.
    """
    table = SymbolTable()
    legacy_builtins = ["String", "Integer", "Boolean", "Float", "Any"]
    for b in legacy_builtins:
        assert table.resolve(b) is not None, f"Legacy built-in {b} must remain supported."

def test_shadowing_regression_protection():
    """
    Ensure the new shadowing policy (preventing local shadowing of globals) 
    protects built-in types as well.
    """
    from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
    from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange
    
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    table.enter_scope("method_scope")
    # Redefining 'Integer' as a variable in a method scope should be rejected
    # to maintain language consistency and prevent confusing regressions.
    entry = SymbolEntry("Integer", SymbolKind.Variable, table.current_scope, node)
    with pytest.raises(SemanticError, match="Shadowing error"):
        table.define(entry)
