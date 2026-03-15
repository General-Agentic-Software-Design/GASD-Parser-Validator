import pytest
from Impl.semantic.SemanticNodes import ResolvedComponentNode, SymbolLink, ResolvedMethodNode, ResolvedParameter, TypeContract, ResolvedResourceNode, ResourceKind, SourceRange
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.DependencyGraphBuilder import DependencyAnalyzer, DependencyKind

def mock_comp(name, deps=None, resources=None, methods=None, pattern="Component"):
    return ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), name, pattern, deps or [], resources or [], methods or {})

def test_semast_dependency_graph():
    analyzer = DependencyAnalyzer(SymbolTable())
    graph = analyzer.analyze([mock_comp("A", deps=[SymbolLink("B")]), mock_comp("B")])
    assert "A" in graph.nodes and "B" in graph.nodes

def test_semast_dependency_analysis():
    analyzer = DependencyAnalyzer(SymbolTable())
    comp = mock_comp("A", deps=[SymbolLink("B")], resources=[ResolvedResourceNode(SourceRange("", 0, 0, 0, 0), "DB", ResourceKind.DB)])
    graph = analyzer.analyze([comp])
    assert len(graph.edges) == 2

def test_semast_architecture_cycles():
    analyzer = DependencyAnalyzer(SymbolTable())
    graph = analyzer.analyze([mock_comp("A", deps=[SymbolLink("B")]), mock_comp("B", deps=[SymbolLink("C")]), mock_comp("C", deps=[SymbolLink("A")])])
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) > 0

def test_semast_resource_linkage():
    analyzer = DependencyAnalyzer(SymbolTable())
    comp = mock_comp("A", resources=[ResolvedResourceNode(SourceRange("", 0, 0, 0, 0), "Q", ResourceKind.CACHE)])
    graph = analyzer.analyze([comp])
    assert graph.edges[0].kind == DependencyKind.USES_RESOURCE

def test_semast_interface_compliance():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    intf = mock_comp("Runnable", methods={"run": ResolvedMethodNode("run", [], TypeContract("Boolean"))}, pattern="Interface")
    table.define(SymbolEntry("Runnable", SymbolKind.Component, table.current_scope, intf))
    impl = mock_comp("MyJob")
    with pytest.raises(SemanticError, match="MissingMethod"):
        analyzer.verify_interface(impl, SymbolLink("Runnable"))

def test_semast_architecture_regression_self_dep():
    analyzer = DependencyAnalyzer(SymbolTable())
    graph = analyzer.analyze([mock_comp("A", deps=[SymbolLink("A")])])
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) == 1
