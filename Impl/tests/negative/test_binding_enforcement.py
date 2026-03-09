import pytest
import os
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Expert Negative Test Suite for US-PARSER-008: GEP-5
Verifies enforcement of mandatory VALIDATE AS TYPE binding.
"""

@pytest.fixture
def api():
    return ParseTreeAPI()

@pytest.fixture
def pipeline():
    return ValidationPipeline()

def test_nt_validate_001_missing_as_type(api):
    """NT-VALIDATE-001: Missing AS TYPE keyword produces syntax error."""
    content = """CONTEXT: "NT"
TARGET: "P"
FLOW F():
    1. VALIDATE user
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() > 0
    # The error should indicate missing AS or similar GEP-5 syntax
    assert any("mismatched" in e.message.lower() or "expect" in e.message.lower() for e in errors.syntax_errors)

def test_nt_validate_002_unknown_type_resolution(api, pipeline):
    """NT-VALIDATE-002: Unknown type path results in semantic error V011."""
    content = """CONTEXT: "NT"
TARGET: "P"
FLOW F():
    1. VALIDATE user AS TYPE.UnknownType
"""
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    
    assert any(e.code == "V011" and "UnknownType" in e.message for e in errors)

def test_nt_validate_003_incomplete_dot_path(api):
    """NT-VALIDATE-003: Dot without type segment produces syntax error."""
    content = """CONTEXT: "NT"
TARGET: "P"
FLOW F():
    1. VALIDATE user AS TYPE.
"""
    _, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_nt_validate_004_missing_type_keyword(api):
    """NT-VALIDATE-004: Missing TYPE keyword in binding produces syntax error."""
    content = """CONTEXT: "NT"
TARGET: "P"
FLOW F():
    1. VALIDATE user AS User
"""
    _, errors = api.parse(content)
    assert errors.get_error_count() > 0

def test_nt_validate_012_semantic_enforcement_missing_binding(api, pipeline):
    """V012: Semantic enforcement if action is VALIDATE but binding is missing (safety check)."""
    from Impl.ast.ASTNodes import FlowStepNode
    # Manually construct a node that might have bypassed grammar (e.g., via generic action fallback)
    # but still has action=="VALIDATE"
    node = FlowStepNode(action="VALIDATE", target="user", asBinding=None, typePath=None, line=1, column=1)
    
    # We bypass ASTGenerator and inject into a dummy file
    from Impl.ast.ASTNodes import GASDFile
    ast = GASDFile(directives=[], decisions=[], types=[], components=[], flows=[], strategies=[], constraints=[], ensures=[], matches=[])
    
    # We use ReferenceResolutionPass directly
    from Impl.validation.passes.ReferenceResolutionPass import ReferenceResolutionPass
    vpass = ReferenceResolutionPass()
    
    # We need a flow to put the step in
    from Impl.ast.ASTNodes import FlowDefinition
    flow = FlowDefinition(name="F", parameters=[], steps=[node], returnType=None, line=1, column=1)
    ast.flows.append(flow)
    
    errors = vpass.validate(ast)
    assert any(e.code == "V012" for e in errors)
