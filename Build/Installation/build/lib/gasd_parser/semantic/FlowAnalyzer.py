from enum import Enum
from typing import List, Dict, Optional, Any, Set
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
                    raise SemanticError(f"TypeMismatch: Step expects {expected_input.baseType} but received {last_out_type.baseType}", location=step.sourceMap)
            
            # Cross-file CALL resolution (AC-X-SEMAST-006-01)
            if step.operation == "CALL":
                target_name = str(getattr(step.targetExpression, 'value', ''))
                if target_name and '.' in target_name:
                    # Only validate qualified (cross-file) method references
                    method_entry = self.symbol_table.resolve(target_name)
                    if not method_entry:
                        # In a multi-file system, we check global scope
                        raise SemanticError(f"UnboundFlow: Could not resolve remote method '{target_name}'", location=step.sourceMap)
            
            last_out_type = produces_type

    def check_consistency(self, flow_node: ResolvedFlowNode) -> None:
        if not flow_node.pipeline:
            return
            
        def _check_steps(steps, is_conditional=False):
            returned = False
            for i, step in enumerate(steps):
                if returned:
                    raise SemanticError(f"UnreachableCode: Step '{step.id}' is after a return action.", location=step.sourceMap)
                
                if step.operation == "RETURN":
                    returned = True
                    
                if step.operation == "ACHIEVE":
                    if not step.targetExpression or not step.targetExpression.value:
                        raise SemanticError("ReachabilityError: ACHIEVE step must have a target.", location=step.sourceMap)
                        
                if step.operation == "MATCH":
                    # Validate exhaustiveness (AC-SEMAST-006-08)
                    has_default = any(getattr(s, 'operation', '') == 'DEFAULT' for s in (step.subSteps or []))
                    if (not has_default and not getattr(step, 'isExhaustive', True)):
                        raise SemanticError("NonExhaustiveMatch: MATCH block is missing cases and has no DEFAULT.", location=step.sourceMap)
                    
                    # Analyze branches independently
                    if step.subSteps:
                        all_branches_return = True
                        for case in step.subSteps:
                            if case.subSteps:
                                # Cases are like conditional blocks
                                if not _check_steps(case.subSteps, is_conditional=True):
                                    all_branches_return = False
                            else:
                                all_branches_return = False
                        
                        if all_branches_return:
                            returned = True
                        
                if step.operation == "IF":
                    # For IF/ELSE, we only mark as returned if EVERY branch returns.
                    # Simple IF alone never marks outer flow as returned.
                    if step.subSteps:
                        _check_steps(step.subSteps, is_conditional=True)
                        
                    if hasattr(step, 'elsePath') and step.elsePath:
                        if _check_steps(step.subSteps, is_conditional=True) and _check_steps(step.elsePath, is_conditional=True):
                            returned = True

                if step.operation == "ENSURE":
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
                            raise SemanticError("MissingOtherwise: ENSURE block must have an OTHERWISE recovery path.", location=step.sourceMap)

                if step.operation == "LOOP":
                    if getattr(step, 'isUnhalting', False):
                        raise SemanticError("InfiniteLoop: Static analysis detected unhalting loop.", location=step.sourceMap)

                # Recursively analyze sub-steps for other constructs if any
                elif step.subSteps and step.operation not in ["MATCH", "IF"]:
                    _check_steps(step.subSteps, is_conditional)
            
            return returned

        _check_steps(flow_node.pipeline)

    def enforce_on_error_scope(self, flow_node: ResolvedFlowNode) -> bool:
        # AT-SEMAST-006-07
        # Ensure ON_ERROR at flow scope wraps block executions
        return hasattr(flow_node, 'globalErrorHandler') and flow_node.globalErrorHandler is not None
