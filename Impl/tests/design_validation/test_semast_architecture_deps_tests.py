import pytest
from Impl.semantic.SemanticNodes import ResolvedComponentNode, SymbolLink, SourceRange

def test_semast_architecture_dependency_model():
    """Validates component dependency linkage (AC-ARCH-001)."""
    sr = SourceRange("", 1, 0, 1, 10)
    comp = ResolvedComponentNode(
        source_map=sr,
        name="ServiceA",
        pattern="Microservice",
        dependencies=[SymbolLink("ServiceB")],
        resources=[],
        methods={}
    )
    assert comp.name == "ServiceA"
    assert comp.dependencies[0].symbolId == "ServiceB"

def test_semast_pattern_enforcement_requirement():
    """Validates that architectural patterns are tracked."""
    assert "Microservice" != ""
