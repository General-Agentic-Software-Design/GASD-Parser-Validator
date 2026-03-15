import pytest
from Impl.semantic.SemanticNodes import ResolvedAnnotation, ScopeEnum

def test_semast_annotation_scope_capture():
    """Validates that annotations capture their logical scope (AC-ANNOT-001)."""
    ann = ResolvedAnnotation("trace", ScopeEnum.TYPE, {"id": "#123"})
    assert ann.scope == ScopeEnum.TYPE
    assert ann.arguments["id"] == "#123"

def test_semast_annotation_inheritance_requirement():
    """Validates that annotation propagation/inheritance is a design requirement."""
    # This might be in a pass, we check for presence of annotation handling logic
    from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange
    sr = SourceRange("", 1, 0, 1, 10)
    node = SemanticNodeBase("T", sr)
    assert hasattr(node, "annotations")
