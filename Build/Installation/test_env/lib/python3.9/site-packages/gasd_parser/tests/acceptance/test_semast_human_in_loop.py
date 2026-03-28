import pytest
from Impl.semantic.SemanticNodes import ResolvedQuestionNode, ResolvedApprovalNode, ResolvedReviewNode, SymbolLink, SourceRange
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.HumanInLoopResolver import HumanInLoopResolver

def test_semast_question_node():
    table = SymbolTable()
    resolver = HumanInLoopResolver(table)
    
    node = ResolvedQuestionNode(SourceRange("", 0, 0, 0, 0), "Is this secure?", True)
    
    # ENSURE "Produces complete ResolvedQuestionNode"
    resolved = resolver.resolve(node)
    assert resolved.kind == "ResolvedQuestion"
    assert resolved.isBlocking is True
    assert len(resolver.blocking_questions) == 1


def test_semast_approval_node():
    table = SymbolTable()
    resolver = HumanInLoopResolver(table)
    
    # Mocking component in symbol table so validation passes
    from Impl.semantic.SemanticNodes import ResolvedComponentNode
    comp = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), "MyComp", "", [], [], {})
    sym = SymbolEntry("MyComp", SymbolKind.Component, table.current_scope, comp)
    table.define(sym)
    
    node = ResolvedApprovalNode(SourceRange("", 0, 0, 0, 0), SymbolLink("MyComp"), "APPROVED", "admin", "2023-10-01")
    
    # ENSURE "Component SymbolLink is verified and timestamps extracted"
    resolver.resolve(node)
    
    approval = resolver.track_approval(SymbolLink("MyComp"))
    assert approval is not None
    assert approval.approver == "admin"


def test_semast_blocking_question():
    table = SymbolTable()
    resolver = HumanInLoopResolver(table)
    
    node = ResolvedQuestionNode(SourceRange("", 0, 0, 0, 0), "Missing auth detail", True)
    resolver.resolve(node)
    
    # ENSURE "System flags deployment constraint violation"
    with pytest.raises(SemanticError, match="DeploymentBlocked"):
        resolver.check_deployment_constraints()


def test_semast_approval_linkage():
    table = SymbolTable()
    resolver = HumanInLoopResolver(table)
    
    node = ResolvedApprovalNode(SourceRange("", 0, 0, 0, 0), SymbolLink("NonExistent"), "APPROVED", "admin", "2023-10-01")
    
    # ENSURE "Symbol resolver fails to hook approval, causing semantic error"
    with pytest.raises(SemanticError, match="ApprovalTargetNotFound"):
        resolver.resolve(node)


def test_semast_human_regression_review():
    table = SymbolTable()
    resolver = HumanInLoopResolver(table)
    
    node = ResolvedReviewNode(SourceRange("", 0, 0, 0, 0), "Check parameter bounds")
    
    # ENSURE "Node preserves exact text without semantic failure"
    resolved = resolver.resolve(node)
    assert resolved.text == "Check parameter bounds"
    assert resolved.kind == "ResolvedReview"
