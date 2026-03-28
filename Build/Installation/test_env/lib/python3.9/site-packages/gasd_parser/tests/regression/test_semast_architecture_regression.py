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
    intf = mock_comp("Runnable", methods={"run": ResolvedMethodNode(SourceRange("", 0, 0, 0, 0), "run", [], TypeContract("Boolean"))}, pattern="Interface")
    table.define(SymbolEntry("Runnable", SymbolKind.Component, table.current_scope, intf))
    impl = mock_comp("MyJob")
    with pytest.raises(SemanticError, match="MissingMethod"):
        analyzer.verify_interface(impl, SymbolLink("Runnable"))

def test_semast_architecture_regression_self_dep():
    analyzer = DependencyAnalyzer(SymbolTable())
    graph = analyzer.analyze([mock_comp("A", deps=[SymbolLink("A")])])
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) == 1

# ===================================================================
# Cross-File Regression Tests
# ===================================================================

def test_semast_architecture_regression_cross_file_interface():
    # RT-X-SEMAST-007-01
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    # Interface in File B
    intf = mock_comp("RemoteIntf", methods={"run": ResolvedMethodNode(SourceRange("", 0, 0, 0, 0), "run", [], TypeContract("Boolean"))}, pattern="Interface")
    table.define(SymbolEntry("RemoteNS.RemoteIntf", SymbolKind.Component, table.global_scope, intf))
    
    # Component in File A implementing it
    impl = mock_comp("LocalImpl")
    
    # Should fail if method missing
    with pytest.raises(SemanticError, match="MissingMethod"):
        analyzer.verify_interface(impl, SymbolLink("RemoteNS.RemoteIntf"))

def test_semast_architecture_regression_cross_file_cycles():
    # RT-X-SEMAST-007-02
    analyzer = DependencyAnalyzer(SymbolTable())
    # A (File1) -> B (File2) -> A (File1)
    a = mock_comp("A", deps=[SymbolLink("B")])
    b = mock_comp("B", deps=[SymbolLink("A")])
    
    graph = analyzer.analyze([a, b])
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) == 1
