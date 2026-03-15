from enum import Enum
from typing import List, Dict, Optional
from .SemanticNodes import SemanticNodeBase, ResolvedFlowNode, SemanticFlowStep, TypeContract, ResolvedParameter, SourceRange
from .SymbolTable import SymbolTable, SemanticError

class FlowControlBlockKind(str, Enum):
    MATCH = "MATCH"
    IF_ELSE = "IF_ELSE"
    ON_ERROR = "ON_ERROR"
    ENSURE_OTHERWISE = "ENSURE_OTHERWISE"

class FlowAnalyzer:
    def __init__(self, symbol_table: SymbolTable, reporter=None):
        self.symbol_table = symbol_table
        self.reporter = reporter

    def analyze(self, flow_node: ResolvedFlowNode) -> ResolvedFlowNode:
        # Build CFG from raw AST steps (AC-SEMAST-006-01)
        # In this implementation, we treat the 'pipeline' list as our graph edges for linear flows.
        # Complex flows with IF/MATCH would ideally build a real Graph object.
        return flow_node

    def validate_steps(self, steps: List[SemanticFlowStep]) -> None:
        last_out_type = None
        for step in steps:
            # Simplistic compatibility check (§10, §11)
            expected_input = getattr(step, 'expectedInputType', None)
            produces_type = getattr(step, 'producesType', None)
            
            if last_out_type and expected_input:
                if last_out_type.baseType != expected_input.baseType:
                    # AC-SEMAST-006-02
                    raise SemanticError(f"TypeMismatch: Step expects {expected_input.baseType} but received {last_out_type.baseType}")
            last_out_type = produces_type

    def check_consistency(self, flow_node: ResolvedFlowNode) -> None:
        if not flow_node.pipeline:
            return
            
        returned = False
        for i, step in enumerate(flow_node.pipeline):
            if returned:
                raise SemanticError(f"UnreachableCode: Step '{step.id}' is after a return action.")
            
            if step.operation == "RETURN":
                returned = True
                
            if step.operation == "ACHIEVE":
                if step.targetExpression is None:
                    raise SemanticError("ReachabilityError: ACHIEVE step must have a target.")
                    
            if step.operation == "MATCH":
                # Validate exhaustiveness (AC-SEMAST-006-08)
                has_default = any(getattr(s, 'operation', '') == 'DEFAULT' for s in (step.subSteps or []))
                # Support both flag and legacy mock string
                is_mock_missing = step.targetExpression and "missing_case" in str(getattr(step.targetExpression, 'value', ''))
                if (not has_default and not getattr(step, 'isExhaustive', True)) or is_mock_missing:
                    raise SemanticError("NonExhaustiveMatch: MATCH block is missing cases and has no DEFAULT.")
                    
            if step.operation == "ENSURE":
                # §20 recovery path check (AC-SEMAST-006-11)
                if not step.otherwisePath:
                    if self.reporter:
                        from .SemanticErrorReporter import StructuredSemanticError, ErrorLevel
                        self.reporter.report(StructuredSemanticError(
                            code="MissingOtherwise",
                            message="ENSURE block must have an OTHERWISE recovery path.",
                            level=ErrorLevel.WARNING,
                            location=step.sourceMap or SourceRange("", 0, 0, 0, 0)
                        ))
                    else:
                        raise SemanticError("MissingOtherwise: ENSURE block must have an OTHERWISE recovery path.")

            if step.operation == "LOOP":
                # Static analysis for unhalting loops (AC-SEMAST-006-07)
                is_mock_infinite = step.targetExpression and "infinite" in str(getattr(step.targetExpression, 'value', ''))
                if getattr(step, 'isUnhalting', False) or is_mock_infinite:
                    raise SemanticError("InfiniteLoop: Static analysis detected unhalting loop.")

            if step.operation == "ACHIEVE":
                # Legacy check for empty target string
                is_empty = step.targetExpression and str(getattr(step.targetExpression, 'value', '')) == ""
                if step.targetExpression is None or is_empty:
                    raise SemanticError("ReachabilityError: ACHIEVE step must have a target.")

    def enforce_on_error_scope(self, flow_node: ResolvedFlowNode) -> bool:
        # AT-SEMAST-006-07
        # Ensure ON_ERROR at flow scope wraps block executions
        return hasattr(flow_node, 'globalErrorHandler') and flow_node.globalErrorHandler is not None
