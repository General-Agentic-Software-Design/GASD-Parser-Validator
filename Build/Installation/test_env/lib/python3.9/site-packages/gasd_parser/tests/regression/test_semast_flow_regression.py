import pytest
from Impl.semantic.SemanticNodes import ResolvedFlowNode, SemanticFlowStep, TypeContract, ResolvedExpression, SourceRange
from Impl.semantic.SymbolTable import SymbolTable, SemanticError
from Impl.semantic.FlowAnalyzer import FlowAnalyzer

def make_step(action, target, target_type="String", produces=None, expected_in=None, handler=None):
    step = SemanticFlowStep(SourceRange("", 0, 0, 0, 0), action, ResolvedExpression("String", TypeContract(target_type), target), {}, None, handler)
    step.expectedInputType = expected_in
    step.producesType = produces
    return step

def test_semast_cfg_generation():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("ACHIEVE", "")])
    assert analyzer.analyze(flow).pipeline[0].operation == "ACHIEVE"

def test_semast_step_compatibility():
    analyzer = FlowAnalyzer(SymbolTable())
    s1 = make_step("CALL", "A", produces=TypeContract("Int"))
    s2 = make_step("CALL", "B", expected_in=TypeContract("Int"))
    analyzer.validate_steps([s1, s2])

def test_semast_unreachable_code():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("RETURN", ""), make_step("CALL", "")])
    with pytest.raises(SemanticError, match="UnreachableCode"):
        analyzer.check_consistency(flow)

def test_semast_achieve_reachability():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("ACHIEVE", "")])
    with pytest.raises(SemanticError, match="ReachabilityError"):
        analyzer.check_consistency(flow)

def test_semast_match_exhaustiveness():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("MATCH", "")])
    analyzer.check_consistency(flow)
    assert len(flow.pipeline) == 1

def test_semast_ensure_otherwise():
    analyzer = FlowAnalyzer(SymbolTable(), version="1.2")
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("ENSURE", "")])
    with pytest.raises(SemanticError, match="MissingOtherwise"):
        analyzer.check_consistency(flow)

def test_semast_on_error_scope():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [])
    flow.globalErrorHandler = "H"
    assert analyzer.enforce_on_error_scope(flow)

def test_semast_cfg_branching():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [make_step("IF", "")])
    analyzer.check_consistency(flow)
    assert len(flow.pipeline) == 1

def test_semast_flow_regression_empty_flow():
    analyzer = FlowAnalyzer(SymbolTable())
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [])
    analyzer.check_consistency(flow)

def test_semast_flow_regression_infinite_loop():
    analyzer = FlowAnalyzer(SymbolTable())
    step = make_step("LOOP", "infinite")
    step.isUnhalting = True
    flow = ResolvedFlowNode(SourceRange("", 0, 0, 0, 0), "F", [], TypeContract("Void"), [step])
    with pytest.raises(SemanticError, match="InfiniteLoop"):
        analyzer.check_consistency(flow)

# ===================================================================
# Cross-File Regression Tests
# ===================================================================

def test_semast_flow_regression_cross_file_binding():
    # RT-X-SEMAST-006-01
    table = SymbolTable()
    analyzer = FlowAnalyzer(table)
    
    # Define remote component method in Global scope
    from Impl.semantic.SemanticNodes import ResolvedMethodNode, ResolvedParameter, SourceRange
    from Impl.semantic.SymbolTable import SymbolEntry, SymbolKind
    remote_res = ResolvedMethodNode(SourceRange("", 0, 0, 0, 0), "remoteMethod", [ResolvedParameter("p", TypeContract("String"))], TypeContract("Boolean"))
    table.define(SymbolEntry("RemoteNS.Comp.remoteMethod", SymbolKind.Method, table.global_scope, remote_res))
    
    # FLOW binds to remote COMPONENT method
    step = make_step("CALL", "RemoteNS.Comp.remoteMethod", expected_in=TypeContract("String"))
    
    # Should pass validation
    analyzer.validate_steps([step])

def test_semast_flow_regression_unbound_error():
    # RT-X-SEMAST-006-02
    analyzer = FlowAnalyzer(SymbolTable())
    step = make_step("CALL", "MissingNS.Comp.method")
    
    with pytest.raises(SemanticError, match="UnboundFlow"):
        analyzer.validate_steps([step])
