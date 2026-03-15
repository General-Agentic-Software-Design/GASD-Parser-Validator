import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticPipeline import SemanticPipeline

def test_semast_flow_analysis_basic():
    """Validates basic flow capture in semantic analysis."""
    content = """CONTEXT: "Test"
TARGET: "T"
FLOW F():
    1. ACHIEVE "Task"
"""
    api = ParseTreeAPI()
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    pipeline = SemanticPipeline()
    system = pipeline.run(ast)
    
    flow = system.namespaces["global"].flows["F"]
    assert flow.name == "F"
    # Basic structural check
    assert hasattr(flow, "pipeline")

def test_semast_flow_analysis_consistency_check():
    """Validates that flow consistency check exists."""
    from Impl.semantic.FlowAnalyzer import FlowAnalyzer
    analyzer = FlowAnalyzer(None)
    assert hasattr(analyzer, "check_consistency")

def test_semast_validate_steps_requirement():
    """Validates that step validation is a design requirement."""
    from Impl.semantic.FlowAnalyzer import FlowAnalyzer
    analyzer = FlowAnalyzer(None)
    assert hasattr(analyzer, "validate_steps")
