import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange

def test_semast_symbol_immutability():
    # ENSURE "It cannot be overwritten in the same scope"
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    entry1 = SymbolEntry("var1", SymbolKind.Variable, table.current_scope, node)
    table.define(entry1)
    
    entry2 = SymbolEntry("var1", SymbolKind.Variable, table.current_scope, node)
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(entry2)

def test_semast_scope_hierarchy():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    # parent scope
    entry1 = SymbolEntry("global_var", SymbolKind.Variable, table.current_scope, node)
    table.define(entry1)
    
    # child scope
    table.enter_scope("child")
    # ENSURE "Child resolves names from parent scope"
    resolved = table.resolve("global_var")
    assert resolved is not None
    assert resolved.name == "global_var"

def test_semast_symbol_definition():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("MyType", SymbolKind.Type, table.current_scope, node)
    entry2 = SymbolEntry("MyComp", SymbolKind.Component, table.current_scope, node)
    
    table.define(entry1)
    table.define(entry2)
    
    assert table.resolve("MyType") is not None
    assert table.resolve("MyComp") is not None

def test_semast_symbol_lookup():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("outer_var", SymbolKind.Variable, table.current_scope, node)
    table.define(entry1)
    
    table.enter_scope("mid")
    table.enter_scope("inner")
    
    resolved = table.resolve("outer_var")
    assert resolved is not None
    assert resolved.name == "outer_var"

def test_semast_scope_isolation():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    table.enter_scope("child")
    entry1 = SymbolEntry("local_var", SymbolKind.Variable, table.current_scope, node)
    table.define(entry1)
    
    assert table.resolve("local_var") is not None
    
    table.exit_scope()
    assert table.resolve("local_var") is None

def test_semast_name_collision():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("duplicate", SymbolKind.Variable, table.current_scope, node)
    table.define(entry1)
    
    entry2 = SymbolEntry("duplicate", SymbolKind.Parameter, table.current_scope, node)
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(entry2)

def test_semast_case_sensitivity():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("User", SymbolKind.Type, table.current_scope, node)
    table.define(entry1)
    
    entry2 = SymbolEntry("user", SymbolKind.Variable, table.current_scope, node)
    table.define(entry2)
    
    assert table.resolve("User") is not None
    assert table.resolve("user") is not None
    assert table.resolve("User") != table.resolve("user")

def test_semast_circular_resolution():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("A", SymbolKind.Type, table.current_scope, node)
    table.define(entry1)
    
    resolution_path = [entry1]
    assert table.check_recursion(entry1, resolution_path) is True

def test_semast_symbol_regression_shadowing():
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    entry1 = SymbolEntry("GlobalType", SymbolKind.Type, table.current_scope, node)
    table.define(entry1)
    
    table.enter_scope("local")
    entry2 = SymbolEntry("GlobalType", SymbolKind.Variable, table.current_scope, node)
    
    with pytest.raises(SemanticError, match="Shadowing error"):
        table.define(entry2)

def test_semast_symbol_regression_missing():
    table = SymbolTable()
    resolved = table.resolve("missing_symbol")
    assert resolved is None

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_cross_file_symbol():
    # AT-X-SEMAST-003-01, AC-X-SEMAST-003-01
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("file1.gasd", 1, 0, 1, 10))
    entry = SymbolEntry("RemoteType", SymbolKind.Type, table.global_scope, node)
    table.define(entry)
    
    # ENSURE "Symbols defined in File A are visible to File B via Global scope"
    resolved = table.resolve("RemoteType")
    assert resolved is not None
    assert resolved.nodeLink.sourceMap.file == "file1.gasd"

def test_semast_cross_file_collision():
    # AT-X-SEMAST-003-02, AC-X-SEMAST-003-03
    table = SymbolTable()
    node1 = SemanticNodeBase("Test", SourceRange("file1.gasd", 1, 0, 1, 10))
    node2 = SemanticNodeBase("Test", SourceRange("file2.gasd", 1, 0, 1, 10))
    
    entry1 = SymbolEntry("ConflictType", SymbolKind.Type, table.global_scope, node1)
    table.define(entry1)
    
    entry2 = SymbolEntry("ConflictType", SymbolKind.Type, table.global_scope, node2)
    # ENSURE "Defining the same symbol in the same namespace across different files is a collision"
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(entry2)

def test_semast_builtin_shadowing():
    # AT-X-SEMAST-003-03, AC-X-SEMAST-003-05
    table = SymbolTable() # Global scope already has built-ins (String, etc.)
    node = SemanticNodeBase("Test", SourceRange("file1.gasd", 1, 0, 1, 10))
    
    # ENSURE "String" is a built-in
    assert table.resolve("String") is not None
    
    entry = SymbolEntry("String", SymbolKind.Type, table.global_scope, node)
    # ENSURE "User defined symbols shadowing built-in types should trigger a warning/error"
    with pytest.raises(SemanticError, match="Collision error|Shadowing error"):
        table.define(entry)
