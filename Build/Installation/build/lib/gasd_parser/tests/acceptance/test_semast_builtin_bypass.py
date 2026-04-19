import pytest
import subprocess
import os
import tempfile
from Impl.semantic.SemanticPipeline import SemanticPipeline
from Impl.semantic.SymbolTable import SemanticError
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def get_semantic_system(files: dict, validate_built_in_types: bool):
    api = ParseTreeAPI()
    asts = []
    for path, content in files.items():
        tree, reporter = api.parse(content)
        if reporter.has_errors():
            raise ValueError(f"Syntax error in {path}")
        ast = ASTGenerator(source_file=path).visit(tree)
        asts.append(ast)
    
    pipeline = SemanticPipeline(validate_built_in_types=validate_built_in_types)
    return pipeline.run(asts)

def test_programmatic_bypass_builtin_types():
    gasd_content = """CONTEXT: "Test"
TARGET: "Py"
TYPE String:
  value: String
"""
    files = {"test_builtin.gasd": gasd_content}
    
    # Should throw error when flag is True
    with pytest.raises(SemanticError, match="BuiltinShadowingError"):
        get_semantic_system(files, validate_built_in_types=True)
        
    # Should NOT throw error when flag is False
    system = get_semantic_system(files, validate_built_in_types=False)
    assert system is not None, "Semantic system should be generated correctly"

def test_cli_bypass_builtin_types():
    gasd_content = """CONTEXT: "Test"
TARGET: "Py"
TYPE String:
  value: String
"""
    with tempfile.NamedTemporaryFile("w", suffix=".gasd", delete=False) as f:
        f.write(gasd_content)
        test_file = f.name
        
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()

        # Default behavior: error
        result_default = subprocess.run(
            ["python3", "-m", "Impl.cli", test_file],
            capture_output=True, text=True, env=env
        )
        assert result_default.returncode != 0
        assert "BuiltinShadowingError" in result_default.stderr

        # Bypass behavior: success
        result_bypass = subprocess.run(
            ["python3", "-m", "Impl.cli", "--no-validate", test_file],
            capture_output=True, text=True, env=env
        )
        assert result_bypass.returncode == 0
        assert "OK Passed" in result_bypass.stderr
    finally:
        os.remove(test_file)
