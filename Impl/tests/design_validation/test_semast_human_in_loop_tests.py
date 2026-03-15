import pytest
from Impl.semantic.SemanticNodes import ResolvedQuestionNode, ResolvedApprovalNode, SourceRange, SymbolLink

def test_semast_human_node_structures():
    """Validates structure for interactive nodes (Question, Approval)."""
    sr = SourceRange("", 1, 0, 1, 10)
    q = ResolvedQuestionNode(sr, "Confirm?")
    assert q.kind == "ResolvedQuestion"
    assert q.text == "Confirm?"
    
    a = ResolvedApprovalNode(sr, SymbolLink("Target"), "PENDING", "Admin", "2026-03-14")
    assert a.kind == "ResolvedApproval"

def test_semast_blocking_requirement_validation():
    """Validates metadata for blocking/non-blocking human involvement."""
    sr = SourceRange("", 1, 0, 1, 10)
    q = ResolvedQuestionNode(sr, "Confirm?", is_blocking=True)
    assert q.isBlocking is True
