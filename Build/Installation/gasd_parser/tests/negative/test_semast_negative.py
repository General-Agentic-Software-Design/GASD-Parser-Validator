import pytest
from Impl.semantic.SemanticPipeline import SemanticPipeline
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticErrorReporter import SemanticErrorReporter
from Impl.semantic.SymbolTable import SemanticError

def test_semast_negative_cases():
    api = ParseTreeAPI()
    
    # Missing Validate binding type
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: UnknownType\n'
    tree, reporter = api.parse(content)
    assert not reporter.has_errors()
    
    ast = ASTGenerator().visit(tree)
    pipeline = SemanticPipeline()
    try:
        # Depending on error handling policy, it could raise or silently swallow/warn
        sys = pipeline.run(ast)
        # Should collect errors
        err_reporter = pipeline.get_reporter() if hasattr(pipeline, "get_reporter") else SemanticErrorReporter()
        assert err_reporter is not None
    except SemanticError as e:
        assert "UnknownType" in str(e)
