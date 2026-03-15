import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange

def make_node():
    return SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))

def test_semast_symbol_immutability():
    table = SymbolTable()
    table.define(SymbolEntry("var1", SymbolKind.Variable, table.current_scope, make_node()))
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(SymbolEntry("var1", SymbolKind.Variable, table.current_scope, make_node()))

def test_semast_scope_hierarchy():
    table = SymbolTable()
    table.define(SymbolEntry("global_var", SymbolKind.Variable, table.current_scope, make_node()))
    table.enter_scope("child")
    assert table.resolve("global_var") is not None

def test_semast_symbol_definition():
    table = SymbolTable()
    table.define(SymbolEntry("MyType", SymbolKind.Type, table.current_scope, make_node()))
    table.define(SymbolEntry("MyComp", SymbolKind.Component, table.current_scope, make_node()))
    assert table.resolve("MyType") is not None
    assert table.resolve("MyComp") is not None

def test_semast_symbol_lookup():
    table = SymbolTable()
    table.define(SymbolEntry("outer", SymbolKind.Variable, table.current_scope, make_node()))
    table.enter_scope("mid")
    table.enter_scope("inner")
    assert table.resolve("outer") is not None

def test_semast_scope_isolation():
    table = SymbolTable()
    table.enter_scope("child")
    table.define(SymbolEntry("local", SymbolKind.Variable, table.current_scope, make_node()))
    assert table.resolve("local") is not None
    table.exit_scope()
    assert table.resolve("local") is None

def test_semast_name_collision():
    table = SymbolTable()
    table.define(SymbolEntry("dup", SymbolKind.Variable, table.current_scope, make_node()))
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(SymbolEntry("dup", SymbolKind.Parameter, table.current_scope, make_node()))

def test_semast_case_sensitivity():
    table = SymbolTable()
    table.define(SymbolEntry("User", SymbolKind.Type, table.current_scope, make_node()))
    table.define(SymbolEntry("user", SymbolKind.Variable, table.current_scope, make_node()))
    assert table.resolve("User") != table.resolve("user")

def test_semast_circular_resolution():
    table = SymbolTable()
    entry = SymbolEntry("A", SymbolKind.Type, table.current_scope, make_node())
    table.define(entry)
    assert table.check_recursion(entry, [entry]) is True

def test_semast_symbol_regression_shadowing():
    table = SymbolTable()
    table.define(SymbolEntry("GlobalType", SymbolKind.Type, table.current_scope, make_node()))
    table.enter_scope("local")
    with pytest.raises(SemanticError, match="Shadowing error"):
        table.define(SymbolEntry("GlobalType", SymbolKind.Variable, table.current_scope, make_node()))

def test_semast_symbol_regression_missing():
    table = SymbolTable()
    assert table.resolve("missing_symbol") is None
