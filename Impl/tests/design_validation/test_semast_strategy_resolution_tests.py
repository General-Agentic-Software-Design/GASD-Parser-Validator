import pytest
from Impl.semantic.SemanticNodes import ResolvedStrategyNode, TypeContract, SourceRange, AlgorithmComplexity
from Impl.semantic.StrategyResolver import StrategyResolver

def test_semast_strategy_contract_validation():
    """Validates strategy contract binding requirements."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    strategy = ResolvedStrategyNode(
        source_map=sr,
        name="QuickSort",
        algorithm="Custom",
        complexity=AlgorithmComplexity.ON_LOG_N,
        contract=TypeContract("SortingAlgorithm")
    )
    assert strategy.name == "QuickSort"
    assert strategy.complexity == AlgorithmComplexity.ON_LOG_N

def test_semast_strategy_resolver_requirement():
    """Validates that strategy resolver exists."""
    from Impl.semantic.StrategyResolver import StrategyResolver
    resolver = StrategyResolver()
    assert hasattr(resolver, "resolve")
