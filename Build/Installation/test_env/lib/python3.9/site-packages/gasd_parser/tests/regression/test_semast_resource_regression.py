import pytest
from Impl.semantic.ResourceResolver import ResourceResolver, SemanticError
from Impl.semantic.SemanticNodes import ResolvedResourceNode, ResourceKind, SourceRange, ResolvedComponentNode, SymbolLink

def test_semast_resource_resolution():
    res = ResourceResolver()
    r = res.resolve("DB1", "DB", "postgres://")
    assert r.resourceKind == ResourceKind.DB
    assert r.uri == "postgres://"
    assert "DB1" in res.resources

def test_semast_resource_linkage():
    res = ResourceResolver()
    r = res.resolve("Storage1", "STORAGE")
    comp = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), "Comp", "Service", [], [r], {})
    res.verify_links(comp) # Should not raise

    comp_bad = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), "Comp", "Service", [], [ResolvedResourceNode(SourceRange("", 0, 0, 0, 0), "Missing", ResourceKind.DB)], {})
    with pytest.raises(SemanticError, match="UnlinkedResource"):
        res.verify_links(comp_bad)

def test_semast_resource_invalid_kind():
    res = ResourceResolver()
    with pytest.raises(SemanticError, match="InvalidResourceKind"):
        res.resolve("R", "NOT_A_KIND")

def test_semast_resource_regression_uri():
    res = ResourceResolver()
    r = res.resolve("API1", "API", uri="invalid_uri")
    assert r.uri == "invalid_uri"
