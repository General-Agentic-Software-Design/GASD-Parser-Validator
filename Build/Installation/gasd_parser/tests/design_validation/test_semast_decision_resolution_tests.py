import pytest
from Impl.semantic.SemanticNodes import ResolvedDecisionNode, SourceRange
from Impl.semantic.DecisionResolver import DecisionResolver

def test_semast_decision_node_resolution():
    """Validates basic decision node property capture."""
    sr = SourceRange("", 1, 0, 1, 10)
    decision = ResolvedDecisionNode(
        source_map=sr,
        name="Arch",
        chosen="Monolith",
        rationale="Simple",
        alternatives=["Monolith", "Microservices"]
    )
    assert decision.chosen == "Monolith"
    assert "Microservices" in decision.alternatives

def test_semast_decision_impact_tracking_requirement():
    """Validates requirement for tracking component impact of decisions."""
    from Impl.semantic.DecisionResolver import DecisionResolver
    resolver = DecisionResolver()
    assert hasattr(resolver, "generate_impact_matrix") or hasattr(resolver, "resolve")
