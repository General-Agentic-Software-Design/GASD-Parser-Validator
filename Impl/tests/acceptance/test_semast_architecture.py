import pytest
from Impl.semantic.SemanticNodes import SemanticNodeBase, ResolvedComponentNode, SymbolLink, ResolvedMethodNode, ResolvedParameter, TypeContract, ResolvedResourceNode, ResourceKind, SourceRange
from Impl.semantic.SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from Impl.semantic.DependencyGraphBuilder import DependencyAnalyzer, DependencyGraph, DependencyEdge, DependencyKind, ComponentNodeType

def generate_mock_component(name: str, methods=None, deps=None, resources=None, pattern="Component") -> ResolvedComponentNode:
    return ResolvedComponentNode(
        source_map=SourceRange("", 0, 0, 0, 0),
        name=name,
        pattern=pattern,
        dependencies=deps or [],
        resources=resources or [],
        methods=methods or {}
    )

def test_semast_dependency_graph():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    comp_a = generate_mock_component("A", deps=[SymbolLink("B")])
    comp_b = generate_mock_component("B")
    
    # ENSURE "DependencyAnalyzer builds valid directed graph"
    graph = analyzer.analyze([comp_a, comp_b])
    
    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert len(graph.edges) == 1
    assert graph.edges[0].source.symbolId == "A"
    assert graph.edges[0].target.symbolId == "B"


def test_semast_dependency_analysis():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    # ENSURE "Edges represent CALLS, EXTENDS, or USES accurately"
    comp_a = generate_mock_component("A", deps=[SymbolLink("B")], resources=[ResolvedResourceNode(SourceRange("", 0, 0, 0, 0), "DB", ResourceKind.DB)])
    
    graph = analyzer.analyze([comp_a])
    assert len(graph.edges) == 2
    
    calls_edge = next(e for e in graph.edges if e.kind == DependencyKind.CALLS)
    uses_edge = next(e for e in graph.edges if e.kind == DependencyKind.USES_RESOURCE)
    
    assert calls_edge.target.symbolId == "B"
    assert uses_edge.target.symbolId == "DB"


def test_semast_interface_compliance():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    # Interface
    intf_methods = {"run": ResolvedMethodNode("run", [], TypeContract("Boolean"))}
    intf_comp = generate_mock_component("Runnable", methods=intf_methods, pattern="Interface")
    
    table.define(SymbolEntry("Runnable", SymbolKind.Component, table.current_scope, intf_comp))
    
    # Implementation (missing 'run')
    impl_comp = generate_mock_component("MyJob")
    
    # ENSURE "Analyzer throws MissingMethod semantic error"
    with pytest.raises(SemanticError, match="MissingMethod"):
        analyzer.verify_interface(impl_comp, SymbolLink("Runnable"))


def test_semast_architecture_cycles():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    # A->B, B->C, C->A
    comp_a = generate_mock_component("A", deps=[SymbolLink("B")])
    comp_b = generate_mock_component("B", deps=[SymbolLink("C")])
    comp_c = generate_mock_component("C", deps=[SymbolLink("A")])
    
    graph = analyzer.analyze([comp_a, comp_b, comp_c])
    
    # ENSURE "Analyzer detects and reports cycle path"
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) > 0
    # The exact path might be A->B->C->A depending on iteration order, but length should be 4
    assert len(cycles[0].path) == 4


def test_semast_dependency_symbol_linking():
    table = SymbolTable()
    
    # Define A in global scope as a remote architectural node
    comp_a = generate_mock_component("A")
    entry_a = SymbolEntry("A", SymbolKind.Component, table.current_scope, comp_a)
    table.define(entry_a)
    
    table.enter_scope("Namespace2")
    comp_b = generate_mock_component("B", deps=[SymbolLink("A")])
    
    # A is global, so B can resolve it
    assert table.resolve("A") is not None


def test_semast_resource_linkage():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    comp_a = generate_mock_component("A", resources=[ResolvedResourceNode(SourceRange("", 0, 0, 0, 0), "MyQueue", ResourceKind.CACHE)])
    graph = analyzer.analyze([comp_a])
    
    # ENSURE "Resource is treated as an edge in DependencyGraph"
    edge = graph.edges[0]
    assert edge.kind == DependencyKind.USES_RESOURCE
    assert edge.target.symbolId == "MyQueue"


def test_semast_interface_mismatch():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    intf_methods = {"run": ResolvedMethodNode("run", [ResolvedParameter("timeout", TypeContract("Integer"))], TypeContract("Boolean"))}
    intf_comp = generate_mock_component("Runnable", methods=intf_methods, pattern="Interface")
    table.define(SymbolEntry("Runnable", SymbolKind.Component, table.current_scope, intf_comp))
    
    # Wrong param type
    impl_methods = {"run": ResolvedMethodNode("run", [ResolvedParameter("timeout", TypeContract("String"))], TypeContract("Boolean"))}
    impl_comp = generate_mock_component("MyJob", methods=impl_methods)
    
    # ENSURE "Semantic Error is raised for interface violation"
    with pytest.raises(SemanticError, match="InterfaceMismatch"):
        analyzer.verify_interface(impl_comp, SymbolLink("Runnable"))


def test_semast_architecture_regression_self_dep():
    table = SymbolTable()
    analyzer = DependencyAnalyzer(table)
    
    comp_a = generate_mock_component("A", deps=[SymbolLink("A")])
    graph = analyzer.analyze([comp_a])
    
    cycles = analyzer.detect_cycles(graph)
    assert len(cycles) == 1
    assert cycles[0].path == ["A", "A"]
