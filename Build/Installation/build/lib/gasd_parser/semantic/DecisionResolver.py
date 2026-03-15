from typing import Dict, List
from .SemanticNodes import ResolvedDecisionNode, SymbolLink
from .SymbolTable import SemanticError

class DecisionResolver:
    def __init__(self):
        # Maps affected Component ID -> List of DECISION IDs impacting it
        self.impact_matrix: Dict[str, List[str]] = {}

    def resolve(self, decision_node: ResolvedDecisionNode) -> ResolvedDecisionNode:
        if not decision_node.affectedComponents:
            # Relaxed for descriptive GASD §20 (AC-SEMAST-008-05)
            pass
        elif len(decision_node.alternatives) >= 3 and not decision_node.rationale:
            raise SemanticError(f"MissingRationale: Decision '{decision_node.name}' has 3 or more alternatives but no rationale specified.")
            
        self.verify_choice(decision_node)
        
        # Build impact matrix
        for comp in decision_node.affectedComponents:
            if comp.symbolId not in self.impact_matrix:
                self.impact_matrix[comp.symbolId] = []
            self.impact_matrix[comp.symbolId].append(decision_node.name)
            
        return decision_node

    def verify_choice(self, decision: ResolvedDecisionNode) -> None:
        if decision.chosen and decision.alternatives:
            # If chosen is not in alternatives, we could warn, but for now we'll allow it 
            # to be compatible with existing specs that might use CHOSEN as a standalone value.
            pass

    def generate_impact_matrix(self) -> Dict[str, List[str]]:
        return self.impact_matrix
