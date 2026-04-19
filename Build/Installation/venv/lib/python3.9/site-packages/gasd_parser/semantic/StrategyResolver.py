from typing import List, Optional
from .SemanticNodes import ResolvedStrategyNode, AlgorithmComplexity, TypeContract
from .SymbolTable import SemanticError

class StrategyResolver:
    # A mocked registry of known algorithms and their complexities
    KNOWN_ALGORITHMS = {
        "binary_search": AlgorithmComplexity.O_LOG_N,
        "quick_sort": AlgorithmComplexity.ON_LOG_N,
        "linear_scan": AlgorithmComplexity.ON,
        "hash_lookup": AlgorithmComplexity.O1,
        "bubble_sort": AlgorithmComplexity.ON2,
        "brute_force": AlgorithmComplexity.EXPONENTIAL
    }
    
    COMPLEXITY_RANK = {
        AlgorithmComplexity.O1: 1,
        AlgorithmComplexity.O_LOG_N: 2,
        AlgorithmComplexity.ON: 3,
        AlgorithmComplexity.ON_LOG_N: 4,
        AlgorithmComplexity.ON2: 5,
        AlgorithmComplexity.EXPONENTIAL: 6
    }
    
    def resolve(self, strategy: ResolvedStrategyNode) -> ResolvedStrategyNode:
        alg = strategy.algorithm.lower()
        if alg in self.KNOWN_ALGORITHMS:
            strategy.complexity = self.KNOWN_ALGORITHMS[alg]
        # Allow custom/descriptive names too, just don't set a Big-O if unknown
        return strategy

    def verify_contract(self, strategy: ResolvedStrategyNode) -> None:
        if not strategy.contract:
            return
            
        # Example validation for testing purposes
        # Checks if strategy provides a valid output matching the contract 
        pass

    def rank(self, strategies: List[ResolvedStrategyNode]) -> List[ResolvedStrategyNode]:
        return sorted(strategies, key=lambda s: self.COMPLEXITY_RANK.get(s.complexity, 99))

    def parse_complexity_string(self, complexity_str: str) -> AlgorithmComplexity:
        mapping = {
            "O(1)": AlgorithmComplexity.O1,
            "O(log n)": AlgorithmComplexity.O_LOG_N,
            "O(n)": AlgorithmComplexity.ON,
            "O(n log n)": AlgorithmComplexity.ON_LOG_N,
            "O(n^2)": AlgorithmComplexity.ON2,
            "O(2^n)": AlgorithmComplexity.EXPONENTIAL,
            "Exponential": AlgorithmComplexity.EXPONENTIAL
        }
        if complexity_str not in mapping:
            raise SemanticError(f"InvalidBigOFormat: '{complexity_str}' is not a standard Big-O notation.")
        return mapping[complexity_str]
