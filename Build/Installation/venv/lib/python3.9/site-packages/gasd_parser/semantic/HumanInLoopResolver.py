from typing import Dict, List, Optional
from .SemanticNodes import SemanticNodeBase, ResolvedQuestionNode, ResolvedApprovalNode, ResolvedReviewNode, SymbolLink
from .SymbolTable import SymbolTable, SemanticError

class HumanInLoopResolver:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.blocking_questions: List[ResolvedQuestionNode] = []
        self.approvals: Dict[str, ResolvedApprovalNode] = {}

    def resolve(self, node: SemanticNodeBase) -> SemanticNodeBase:
        if isinstance(node, ResolvedQuestionNode):
            if node.isBlocking:
                self.blocking_questions.append(node)
                
        elif isinstance(node, ResolvedApprovalNode):
            # Verify the target exists
            target_symbol = self.symbol_table.resolve(node.target.symbolId)
            if not target_symbol:
                raise SemanticError(f"ApprovalTargetNotFound: Cannot link approval to undefined symbol '{node.target.symbolId}'.")
                
            self.approvals[node.target.symbolId] = node
            
        elif isinstance(node, ResolvedReviewNode):
            pass # "Node preserves exact text without semantic failure"
            
        return node

    def track_approval(self, target: SymbolLink) -> Optional[ResolvedApprovalNode]:
        return self.approvals.get(target.symbolId)

    def check_deployment_constraints(self) -> None:
        if self.blocking_questions:
            # AC-SEMAST-014-05: Blocking QUESTIONS MUST prevent system deployment if unresolved
            raise SemanticError(f"DeploymentBlocked: There are {len(self.blocking_questions)} unresolved blocking questions.")
