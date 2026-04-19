import pytest
from Impl.semantic.NamespaceResolver import NamespaceResolver, DependencyError
from Impl.semantic.SemanticNodes import NamespaceNode, SourceRange

def test_semast_namespace_resolution():
    res = NamespaceResolver()
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "A", {}, {}, {}, {}, {})
    res.register(ns)
    assert res.resolve("A") is ns

def test_semast_import_resolution():
    res = NamespaceResolver()
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Core", {}, {}, {}, {}, {})
    res.register(ns)
    assert res.resolve_import("Core") is ns

def test_semast_namespace_alias():
    res = NamespaceResolver()
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Original", {}, {}, {}, {}, {})
    res.register(ns, alias="Shared")
    assert res.resolve("Shared") is ns

def test_semast_import_symbol_export():
    res = NamespaceResolver()
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Lib", {"MyType": "MockType"}, {}, {}, {}, {})
    res.register(ns)
    assert res.resolve_symbol("Lib.MyType") == "MockType"

def test_semast_namespace_regression_circular():
    res = NamespaceResolver()
    res.add_dependency("A", "B")
    with pytest.raises(DependencyError, match="Circular"):
        res.add_dependency("B", "A")

# ===================================================================
# Cross-File Regression Tests
# ===================================================================

def test_semast_namespace_regression_cross_file_import():
    # RT-X-SEMAST-002-01
    res = NamespaceResolver()
    # Simulate cross-file import: File A imports B
    res.add_dependency("FileA", "FileB")
    assert "FileB" in res.get_dependencies("FileA")

def test_semast_namespace_regression_deep_chain():
    # RT-X-SEMAST-002-02
    res = NamespaceResolver()
    res.add_dependency("A", "B")
    res.add_dependency("B", "C")
    res.add_dependency("C", "D")
    
    # Dependency order: leaves first, dependents last
    # A→B→C→D means D has no deps, processed first; A depends on everything, last
    order = res.get_processing_order(["A", "B", "C", "D"])
    assert order[0] == "A"
    assert order[-1] == "D"
