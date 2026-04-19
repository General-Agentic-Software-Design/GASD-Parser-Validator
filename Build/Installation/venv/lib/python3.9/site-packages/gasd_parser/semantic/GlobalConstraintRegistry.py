from typing import List, Dict
from .SemanticNodes import ResolvedConstraintNode, SymbolLink

class GlobalConstraintRegistry:
    def __init__(self):
        self.constraints: List[ResolvedConstraintNode] = []
        self.scope_mappings: Dict[str, List[ResolvedConstraintNode]] = {}

    def register(self, constraint: ResolvedConstraintNode):
        self.constraints.append(constraint)
        # In a real impl, we'd map to affected scopes/symbols
        pass

    def get_all_constraints(self) -> List[ResolvedConstraintNode]:
        return self.constraints
