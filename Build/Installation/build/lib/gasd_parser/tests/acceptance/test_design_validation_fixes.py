"""
Acceptance tests for Design Validation Fixes (Self-Hosting).
"""
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_standalone_flow_annotation_visit():
    api = ParseTreeAPI()
    content = """FLOW f():
    @trace #1
    1. LOG "step"
    @trace #2
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    steps = ast.flows[0].steps
    assert len(steps) == 3
    assert steps[0].action == "ANNOTATION"
    assert steps[1].stepNumber == 1
    assert steps[2].action == "ANNOTATION"

def test_otherwise_return():
    api = ParseTreeAPI()
    content = """FLOW f():
    1. ENSURE true
        OTHERWISE RETURN "failure"
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    step = ast.flows[0].steps[0]
    assert len(step.subSteps) == 1
    assert step.subSteps[0].action == "OTHERWISE"
    assert "RETURN" in step.subSteps[0].target

def test_create_block():
    api = ParseTreeAPI()
    content = """FLOW f():
    1. CREATE Type:
        field1: "val1"
        field2: 42
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    
    generator = ASTGenerator()
    ast = generator.visit(tree)
    
    step = ast.flows[0].steps[0]
    assert step.action == "CREATE"
    assert step.target.startswith("Type")
    assert len(step.subSteps) == 2
    assert step.subSteps[0].action == "PROPERTY"
    assert "field1" in step.subSteps[0].target
    assert "field2" in step.subSteps[1].target
