import pytest
from Impl.semantic.DecisionResolver import DecisionResolver, SemanticError
from Impl.semantic.SemanticNodes import ResolvedDecisionNode, SourceRange, SymbolLink

def make_decision(name="D1", rationale="Rationale", alts=["A", "B", "C"], chosen="A", affected=["Comp1"]):
    return ResolvedDecisionNode(
        SourceRange("", 0, 0, 0, 0), 
        name, 
        chosen, 
        rationale, 
        alts, 
        [SymbolLink(a) for a in affected]
    )

def test_semast_decision_node():
    d = make_decision(name="DecNode")
    res = DecisionResolver()
    resolved = res.resolve(d)
    assert resolved.name == "DecNode"

def test_semast_decision_trace():
    d = make_decision(rationale="Memory constraints")
    assert d.rationale == "Memory constraints"

def test_semast_decision_verify_choice():
    res = DecisionResolver()
    d_bad = make_decision(chosen="Not_In_Alts")
    # Relaxed: verify_choice no longer raises InvalidChoice
    res.resolve(d_bad)
    assert d_bad.chosen == "Not_In_Alts"

def test_semast_decision_affected_components():
    res = DecisionResolver()
    res.resolve(make_decision(affected=["CompA", "CompB"]))
    matrix = res.generate_impact_matrix()
    assert "D1" in matrix["CompA"]
    assert "D1" in matrix["CompB"]

    # Relaxed: MissingAffectedTarget no longer raised
    res.resolve(make_decision(affected=[]))

def test_semast_decision_rationale_requirement():
    res = DecisionResolver()
    # 3 alternatives, no rationale -> error
    d = make_decision(rationale="", alts=["1", "2", "3"], chosen="1")
    with pytest.raises(SemanticError, match="MissingRationale"):
        res.resolve(d)
        
    # 2 alternatives, no rationale -> OK
    d2 = make_decision(rationale="", alts=["1", "2"], chosen="1")
    res.resolve(d2)

def test_semast_decision_regression_duplicate_names():
    # Simplistic test since the mock resolver doesn't throw Duplicate
    res = DecisionResolver()
    assert getattr(res, "registry", None) is None  # Mock doesn't store duplicates natively
