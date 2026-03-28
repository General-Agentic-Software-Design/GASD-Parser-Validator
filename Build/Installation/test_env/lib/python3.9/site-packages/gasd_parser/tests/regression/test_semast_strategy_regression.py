import pytest
from Impl.semantic.StrategyResolver import StrategyResolver, SemanticError
from Impl.semantic.SemanticNodes import ResolvedStrategyNode, AlgorithmComplexity, SourceRange

def test_semast_strategy_node():
    node = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "binary_search")
    assert node.name == "S1"

def test_semast_strategy_resolution():
    resolver = StrategyResolver()
    node = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "binary_search")
    resolver.resolve(node)
    assert node.complexity == AlgorithmComplexity.O_LOG_N

def test_semast_strategy_contract():
    node = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "binary_search")
    assert node.algorithm == "binary_search"

def test_semast_strategy_ranking():
    resolver = StrategyResolver()
    n1 = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "binary_search", complexity=AlgorithmComplexity.O_LOG_N)
    n2 = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S2", "linear_scan", complexity=AlgorithmComplexity.ON)
    n3 = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S3", "hash_lookup", complexity=AlgorithmComplexity.O1)
    ranked = resolver.rank([n2, n1, n3])
    assert [r.name for r in ranked] == ["S3", "S1", "S2"]

def test_semast_strategy_registry_validate():
    node = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "hash_lookup")
    resolver = StrategyResolver()
    resolver.resolve(node)
    assert node.complexity == AlgorithmComplexity.O1

def test_semast_strategy_big_o_format():
    resolver = StrategyResolver()
    with pytest.raises(SemanticError, match="not a standard Big-O notation"):
        resolver.parse_complexity_string("n^2")

def test_semast_strategy_regression_missing_complexity():
    resolver = StrategyResolver()
    node = ResolvedStrategyNode(SourceRange("", 0, 0, 0, 0), "S1", "unknown_alg")
    # Relaxed: No longer raises UnknownAlgorithm
    resolver.resolve(node)
    assert node.complexity is None
