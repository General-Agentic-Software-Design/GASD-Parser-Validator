"""
Acceptance tests for Directives (NAMESPACE, IMPORT) and Reference Resolution (Warnings).
"""
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.passes.ReferenceResolutionPass import ReferenceResolutionPass

def test_namespace_and_import_visit():
    """Verifies that NAMESPACE and IMPORT directives are correctly stored in the AST."""
    api = ParseTreeAPI()
    content = """NAMESPACE: "com.example.system"
IMPORT "lib.core"
IMPORT "lib.utils" AS Utils
CONTEXT: "Test"
TARGET: "Python3"
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    directives = {d.directiveType: d for d in ast.directives}
    assert "NAMESPACE" in directives
    assert directives["NAMESPACE"].values == ["com.example.system"]
    
    # Imports
    imports = [d for d in ast.directives if d.directiveType == "IMPORT"]
    assert len(imports) == 2
    assert imports[0].values == ["lib.core"]
    assert imports[0].alias is None
    assert imports[1].values == ["lib.utils"]
    assert imports[1].alias == "Utils"

def test_reference_resolution_warnings():
    """Verifies that unknown types/dependencies are reported as warnings, not errors."""
    api = ParseTreeAPI()
    content = """CONTEXT: "WarningTest"
TARGET: "Python3"
TYPE Node:
    ref: UnknownType
COMPONENT Comp:
    DEPENDENCIES: [ExternalLib]
    INTERFACE:
        action(p: UnknownParamType) -> UnknownReturnType
"""
    tree, errors = api.parse(content)
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    validator = ReferenceResolutionPass()
    semantic_errors = validator.validate(ast)
    
    # Should have warnings for UnknownType, ExternalLib, UnknownParamType, UnknownReturnType
    # (Note: check_type_expr is called twice for parameters/returns)
    warnings = [e for e in semantic_errors if e.severity == "WARNING"]
    codes = {e.code for e in warnings}
    
    assert "V008" in codes # Unknown Type
    assert "V009" in codes # Unknown Dependency
    assert all(e.severity == "WARNING" for e in semantic_errors)
    
    # Verify ErrorReporter counts them correctly
    from Impl.errors.ErrorReporter import ErrorReporter
    reporter = ErrorReporter()
    for e in semantic_errors:
        reporter.add_semantic_error(e)
    
    assert reporter.get_error_count() == 0
    assert reporter.get_warning_count() > 0
    assert reporter.has_errors() == False
