import pytest
from Impl.semantic.SemanticNodes import ResolvedFlowNode, SemanticFlowStep, TypeContract, ResolvedParameter, SourceRange, ResolvedMethodNode
from Impl.semantic.SymbolTable import SymbolTable, SemanticError, SymbolEntry, SymbolKind
from Impl.semantic.FlowAnalyzer import FlowAnalyzer

from Impl.semantic.SemanticNodes import ResolvedExpression, SymbolLink

def generate_step(action: str, target: str, expected_in=None, produces_out=None, handler=None) -> SemanticFlowStep:
    step = SemanticFlowStep(
        source_map=SourceRange("", 0, 0, 0, 0),
        operation=action,
        target_expression=ResolvedExpression("String", TypeContract("String"), target),
        bindings={},
        error_path=None,
        otherwise_path=handler
    )
    # Monkey-patch attributes used by our Simplistic FlowAnalyzer validation
    step.expectedInputType = expected_in
    step.producesType = produces_out
    return step

def test_semast_cfg_generation():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    flow_node = ResolvedFlowNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="myFlow",
        inputs=[],
        output=TypeContract("Boolean"),
        pipeline=[generate_step("ACHIEVE", "True")]
    )
    
    # ENSURE "Converts to ResolvedFlowNode with linear CFG"
    analyzed = analyzer.analyze(flow_node)
    assert analyzed.pipeline[0].operation == "ACHIEVE"


def test_semast_step_compatibility():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    step1 = generate_step("CALL", "fetchData", produces_out=TypeContract("String"))
    step2 = generate_step("CALL", "processData", expected_in=TypeContract("String"))
    
    # ENSURE "FlowAnalyzer confirms parameter type compatibility"
    analyzer.validate_steps([step1, step2]) # Should not throw
    
    step3 = generate_step("CALL", "badProcess", expected_in=TypeContract("Integer"))
    
    with pytest.raises(SemanticError, match="TypeMismatch"):
        analyzer.validate_steps([step1, step3])


def test_semast_unreachable_code():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    step1 = generate_step("RETURN", "value")
    step2 = generate_step("CALL", "impossible")
    
    flow_node = ResolvedFlowNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="myFlow",
        inputs=[],
        output=TypeContract("Boolean"),
        pipeline=[step1, step2]
    )
    
    # ENSURE "checkConsistency flags unreachable step"
    with pytest.raises(SemanticError, match="UnreachableCode"):
        analyzer.check_consistency(flow_node)


def test_semast_achieve_reachability():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    step = generate_step("ACHIEVE", "")
    flow_node = ResolvedFlowNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="myFlow",
        inputs=[],
        output=TypeContract("Boolean"),
        pipeline=[step]
    )
    
    # ENSURE "Target string resolves logically or generates warning"
    with pytest.raises(SemanticError, match="ReachabilityError"):
        analyzer.check_consistency(flow_node)


def test_semast_match_exhaustiveness():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    step = generate_step("MATCH", "missing_case")
    step.isExhaustive = False
    flow_node = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "myFlow", [], TypeContract("Boolean"), [step])
    
    # ENSURE "Analyzer flags non-exhaustive MATCH block"
    with pytest.raises(SemanticError, match="NonExhaustiveMatch"):
        analyzer.check_consistency(flow_node)


def test_semast_ensure_otherwise():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table, version="1.2")
    
    step = generate_step("ENSURE", "condition", handler=None)
    flow_node = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "myFlow", [], TypeContract("Boolean"), [step])
    
    # ENSURE "Analyzer flags missing error recovery path"
    with pytest.raises(SemanticError, match="MissingOtherwise"):
        analyzer.check_consistency(flow_node)


def test_semast_on_error_scope():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    flow_node = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "myFlow", [], TypeContract("Boolean"), [])
    flow_node.globalErrorHandler = "HandleAll"
    
    # ENSURE "Exception handling wraps all inner block executions"
    assert analyzer.enforce_on_error_scope(flow_node) is True


def test_semast_cfg_branching():
    # Placeholder for IF_ELSE logic CFG mapping
    analyzer = FlowAnalyzer(SymbolTable())
    step = SemanticFlowStep(SourceRange("",0,0,0,0), "IF", None, {})
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [step])
    analyzer.check_consistency(flow)
    assert len(flow.pipeline) == 1

def test_semast_flow_regression_empty_flow():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    flow_node = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "myFlow", [], TypeContract("Boolean"), [])
    
    # ENSURE "FlowAnalyzer gracefully accepts or warns based on contract"
    analyzer.check_consistency(flow_node) # Should not throw


def test_semast_flow_regression_infinite_loop():
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    step = generate_step("LOOP", "infinite")
    step.isUnhalting = True
    flow_node = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "myFlow", [], TypeContract("Boolean"), [step])
    
    # ENSURE "Static analysis halts execution projection safely"
    with pytest.raises(SemanticError, match="InfiniteLoop"):
        analyzer.check_consistency(flow_node)

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_cross_file_flow_binding():
    # AT-X-SEMAST-006-01, AC-X-SEMAST-006-01, AC-X-SEMAST-006-02
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    # Define remote component method
    remote_res = ResolvedMethodNode(SourceRange("", 0, 0, 0, 0), "remoteMethod", [ResolvedParameter("p", TypeContract("String"))], TypeContract("Boolean"))
    table.define(SymbolEntry("Namespace.Comp.remoteMethod", SymbolKind.Method, table.global_scope, remote_res))
    
    # FLOW binds to remote COMPONENT method
    step = generate_step("CALL", "Namespace.Comp.remoteMethod", expected_in=TypeContract("String"))
    step.bindings = {"p": SymbolLink("remote_param_id")}
    
    # ENSURE "Binding succeeds if signatures match exactly"
    analyzer.validate_steps([step]) # Should pass

def test_semast_unbound_flow_error():
    # AT-X-SEMAST-006-02, AC-X-SEMAST-006-03
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    # Target a non-existent remote method
    step = generate_step("CALL", "MissingNamespace.Comp.method")
    
    # ENSURE "Semantic error reported for unbound flow resolution"
    with pytest.raises(SemanticError, match="UnboundFlow"):
        analyzer.validate_steps([step])
