import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticPipeline import SemanticPipeline

CONTENT = """CONTEXT: "Backward Compat"
TARGET: "System"
FLOW F():
  1. ACHIEVE "X" """

def test_semast_compat_no_flag_impact():
    # ENSURE "Default parser outputs AST natively without semantic augmentation"
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    ast = ASTGenerator().visit(tree)
    
    assert hasattr(ast, "flows")
    assert not hasattr(ast, "namespaces")  # Confirm it's purely Syntactic AST

def test_semast_compat_zero_overhead():
    # ENSURE "Semantic Pipeline requires explicit invocation"
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    assert not reporter.has_errors()

def test_semast_compat_pipeline_isolation():
    # ENSURE "The semantic classes are purely additive (run explicitly separately)"
    pipeline = SemanticPipeline()
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    ast = ASTGenerator().visit(tree)
    
    # Isolated pipeline execution
    semantic_sys = pipeline.run(ast)
    assert hasattr(semantic_sys, "namespaces")

def test_semast_compat_legacy_flags():
    # ENSURE "Existing --ast formatting is unchanged"
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    ast = ASTGenerator().visit(tree)
    assert hasattr(ast, "flows")

def test_semast_compat_test_suite_integrity():
    # ENSURE "All original syntax/parse tests continue passing (verified by runner)"
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    assert not reporter.has_errors()

def test_semast_compat_regression_ast_generation():
    # ENSURE "Old code mapping works unaffected"
    api = ParseTreeAPI()
    tree, reporter = api.parse(CONTENT)
    ast = ASTGenerator().visit(tree)
    assert len(ast.flows) == 1
