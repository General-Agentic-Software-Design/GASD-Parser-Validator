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
