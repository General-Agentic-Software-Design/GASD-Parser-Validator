import pytest
from Impl.semantic.HumanInLoopResolver import HumanInLoopResolver
from Impl.semantic.SemanticNodes import ResolvedQuestionNode, ResolvedApprovalNode, ResolvedReviewNode, SourceRange, SymbolLink
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError

def test_semast_question_node():
    q = ResolvedQuestionNode(SourceRange("", 0, 0, 0, 0), "Prompt?", False)
    assert q.text == "Prompt?"
    assert q.isBlocking is False

def test_semast_approval_node():
    a = ResolvedApprovalNode(SourceRange("", 0, 0, 0, 0), SymbolLink("TargetType"), "Admin", "User1", "2026-01-01")
    assert a.approver == "User1"
    assert a.target.symbolId == "TargetType"

def test_semast_blocking_question():
    q = ResolvedQuestionNode(SourceRange("", 0, 0, 0, 0), "Really?", True)
    resolver = HumanInLoopResolver(SymbolTable())
    resolver.resolve(q)
    assert q in resolver.blocking_questions
    with pytest.raises(SemanticError, match="DeploymentBlocked"):
        resolver.check_deployment_constraints()

def test_semast_approval_linkage():
    table = SymbolTable()
    # Stub the target so we don't get 'not found' error
    table.define(SymbolEntry("Comp1", SymbolKind.Component, table.current_scope, None)) # type: ignore
    resolver = HumanInLoopResolver(table)
    a = ResolvedApprovalNode(SourceRange("", 0, 0, 0, 0), SymbolLink("Comp1"), "Role", "App", "Time")
    resolver.resolve(a)
    assert resolver.track_approval(SymbolLink("Comp1")) == a

def test_semast_human_regression_review():
    r = ResolvedReviewNode(SourceRange("", 0, 0, 0, 0), "Looks good")
    resolver = HumanInLoopResolver(SymbolTable())
    res = resolver.resolve(r)
    assert res == r
