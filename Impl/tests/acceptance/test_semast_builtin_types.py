import pytest
from Impl.semantic.SymbolTable import SymbolTable, SymbolKind

def test_builtin_types_registration_exhaustive():
    """
    AT-SEMAST-019-01: Verify all 15 built-in types are pre-registered in global scope.
    This test explicitly checks each type to ensure absolute coverage.
    """
    table = SymbolTable()
    builtins = [
        "String", "Integer", "Int", "Boolean", "Float", "Decimal", "Bytes", "UUID", 
        "DateTime", "Optional", "List", "Map", "Enum", "Result", "Any", "Void"
    ]
    for b in builtins:
        resolved = table.resolve(b)
        assert resolved is not None, f"Built-in type {b} should be pre-registered"
        assert resolved.kind == SymbolKind.Type
        assert resolved.scope == table.global_scope

def test_builtin_type_collision():
    """
    AT-SEMAST-019-05: Verify collision error when attempting to redefine a built-in type.
    """
    from Impl.semantic.SymbolTable import SymbolEntry, SemanticError
    from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange
    
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    # Attempt to define 'String' in global scope
    entry = SymbolEntry("String", SymbolKind.Type, table.global_scope, node)
    with pytest.raises(SemanticError, match="Collision error|already defined"):
        table.define(entry)

def test_builtin_type_shadowing_prevention():
    """
    Verify that built-in types cannot be shadowed in local scopes (consistent with US-SEMAST-020).
    """
    from Impl.semantic.SymbolTable import SymbolEntry, SemanticError
    from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange
    
    table = SymbolTable()
    node = SemanticNodeBase("Test", SourceRange("", 0, 0, 0, 0))
    
    table.enter_scope("local_scope")
    entry = SymbolEntry("String", SymbolKind.Type, table.current_scope, node)
    
    # Should raise Shadowing error because 'String' exists in outer (global) scope
    with pytest.raises(SemanticError, match="Shadowing error"):
        table.define(entry)

def test_reference_resolution_all_builtins_explicit():
    """
    AT-SEMAST-019-01: Reference resolution (V008) should not produce warnings for ANY built-in.
    This test iterates over all 15 types to ensure they are all in the 'primitive_types' set.
    """
    from Impl.validation.passes.ReferenceResolutionPass import ReferenceResolutionPass
    from Impl.ast.ASTNodes import GASDFile, TypeDefinition, FieldNode, TypeExpression
    
    builtins = [
        "String", "Integer", "Int", "Boolean", "Float", "Decimal", "Bytes", "UUID", 
        "DateTime", "Optional", "List", "Map", "Enum", "Result", "Any", "Void"
    ]
    
    pass_obj = ReferenceResolutionPass()
    
    for b in builtins:
        # Create a field with the specific built-in type
        tx = TypeExpression(baseType=b)
        field = FieldNode(f"field_{b}", tx)
        type_def = TypeDefinition(f"Container_{b}", [field])
        file_ast = GASDFile(types=[type_def])
        
        errors = pass_obj.validate(file_ast)
        # Ensure no V008 warnings for this specific built-in
        assert not any(e.code == 'V008' and b in e.message for e in errors), f"Type {b} should be recognized as primitive"

def test_reference_resolution_builtin_complex_result():
    """
    AT-SEMAST-019-02: Structural types (Result) resolve correctly with arguments.
    """
    from Impl.validation.passes.ReferenceResolutionPass import ReferenceResolutionPass
    from Impl.ast.ASTNodes import GASDFile, TypeDefinition, FieldNode, TypeExpression
    
    # Result<String>
    inner_tx = TypeExpression(baseType="String")
    type_expr = TypeExpression(baseType="Result", genericArgs=[inner_tx])
    field = FieldNode("operation_result", type_expr)
    type_def = TypeDefinition("Outcome", [field])
    file_ast = GASDFile(types=[type_def])
    
    pass_obj = ReferenceResolutionPass()
    errors = pass_obj.validate(file_ast)
    
    assert not any(e.code == 'V008' for e in errors)
