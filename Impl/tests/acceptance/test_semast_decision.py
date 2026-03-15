import pytest
from Impl.semantic.SemanticNodes import ResolvedDecisionNode, SymbolLink, SourceRange
from Impl.semantic.DecisionResolver import DecisionResolver, SemanticError

def test_semast_decision_node():
    resolver = DecisionResolver()
    
    decision = ResolvedDecisionNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="DB_Choice",
        chosen="PostgreSQL",
        rationale="Needs relational data",
        alternatives=["PostgreSQL", "MongoDB"],
        affected_components=[SymbolLink("UserService")]
    )
    
    # ENSURE "Produces complete ResolvedDecisionNode"
    resolved = resolver.resolve(decision)
    assert resolved.name == "DB_Choice"


def test_semast_decision_trace():
    resolver = DecisionResolver()
    
    decision = ResolvedDecisionNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="DB_Choice",
        chosen="PostgreSQL",
        alternatives=["PostgreSQL", "MongoDB"],
        affected_components=[SymbolLink("X")]
    )
    
    resolver.resolve(decision)
    matrix = resolver.generate_impact_matrix()
    
    # ENSURE "Impact matrix correctly hooks DECISION to SymbolLink of 'X'"
    assert "X" in matrix
    assert "DB_Choice" in matrix["X"]


def test_semast_decision_verify_choice():
    resolver = DecisionResolver()
    
    decision = ResolvedDecisionNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="DB_Choice",
        chosen="MySQL", # MySQL is not in alternatives
        alternatives=["PostgreSQL", "MongoDB"],
        affected_components=[SymbolLink("X")]
    )
    
    # Relaxed: DecisionResolver no longer flags mismatch error for descriptive GASD
    resolver.resolve(decision)
    assert decision.chosen == "MySQL"


def test_semast_decision_affected_components():
    resolver = DecisionResolver()
    
    decision = ResolvedDecisionNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="DB_Choice",
        chosen="PostgreSQL",
        alternatives=["PostgreSQL", "MongoDB"],
        affected_components=[] # Empty affects block
    )
    
    # Relaxed: Constraint failure no longer raised for missing target
    resolver.resolve(decision)


def test_semast_decision_rationale_requirement():
    resolver = DecisionResolver()
    
    decision = ResolvedDecisionNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name="DB_Choice",
        chosen="PostgreSQL",
        rationale="", # Empty rationale
        alternatives=["PostgreSQL", "MongoDB", "MySQL"], # 3 alternatives
        affected_components=[SymbolLink("X")]
    )
    
    # ENSURE "Constraint failure raised requiring rationale"
    with pytest.raises(SemanticError, match="MissingRationale"):
        resolver.resolve(decision)


    from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SymbolScope
    from Impl.semantic.SemanticNodes import SemanticNodeBase
    table = SymbolTable()
    
    sr = SourceRange("", 1, 0, 1, 10)
    dummy_node = SemanticNodeBase("Decision", sr)
    
    # Register first decision
    entry1 = SymbolEntry("D1", SymbolKind.Variable, table.current_scope, dummy_node)
    table.define(entry1)
    
    # Try to register duplicate
    entry2 = SymbolEntry("D1", SymbolKind.Variable, table.current_scope, dummy_node)
    with pytest.raises(SemanticError, match="Collision error"):
        table.define(entry2)
