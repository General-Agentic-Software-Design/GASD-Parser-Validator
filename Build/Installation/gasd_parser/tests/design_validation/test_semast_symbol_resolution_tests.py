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
