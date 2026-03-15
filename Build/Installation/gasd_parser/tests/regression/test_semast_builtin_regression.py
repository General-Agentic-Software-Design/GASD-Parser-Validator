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

def test_cli_backward_compatibility_gasd_builtin():
    """
    RT-SEMAST-020-01: Verify that a standard GASD file with built-in types passes validation
    via CLI without any changes to existing behavior.
    """
    import subprocess
    import os
    
    # Use a real example file from the repo
    example_file = "Specs/examples/validate_simple.gasd"
    if not os.path.exists(example_file):
        pytest.skip(f"Example file {example_file} not found")
        
    env = os.environ.copy()
    env["PYTHONPATH"] = "Build/Installation"
    
    # Run gasd-parser without --ast-sem (default behavior)
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", example_file],
        capture_output=True, text=True, env=env
    )
    
    assert result.returncode == 0
    assert "OK Passed" in result.stderr
    # Ensure no V008 warnings for 'Result' which is now a built-in
    assert "V008" not in result.stderr

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
