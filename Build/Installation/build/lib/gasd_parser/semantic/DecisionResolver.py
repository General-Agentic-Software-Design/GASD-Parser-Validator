from typing import Dict, List, Optional
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
            # Auto-detect conflicts when multiple decisions affect the same symbol
            if len(self.impact_matrix[comp.symbolId]) > 1:
                raise SemanticError(f"DecisionConflict: Multiple decisions {self.impact_matrix[comp.symbolId]} affect the same symbol '{comp.symbolId}'.")
            
        return decision_node

    def verify_choice(self, decision: ResolvedDecisionNode) -> None:
        if decision.chosen and decision.alternatives:
            # If chosen is not in alternatives, we could warn, but for now we'll allow it 
            # to be compatible with existing specs that might use CHOSEN as a standalone value.
            pass

    def detect_conflicts(self):
        # US-X-SEMAST-008: Decision conflict detection
        for comp_id, decision_ids in self.impact_matrix.items():
            if len(decision_ids) > 1:
                # Multiple decisions affecting the same component/symbol
                raise SemanticError(f"DecisionConflict: Multiple decisions {decision_ids} affect the same symbol '{comp_id}'.")

    def generate_impact_matrix(self) -> Dict[str, List[str]]:
        """Return the impact matrix mapping component IDs to decision IDs that affect them."""
        return dict(self.impact_matrix)
