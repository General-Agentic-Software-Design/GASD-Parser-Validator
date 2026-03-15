import pytest
from Impl.semantic.SemanticNodes import ResolvedResourceNode, ResourceKind, SourceRange

def test_semast_resource_resolution_core():
    """Validates resource identification and kind mapping."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    res = ResolvedResourceNode(sr, "Database", ResourceKind.DB, "sql://localhost")
    assert res.resourceKind == ResourceKind.DB
    assert res.uri == "sql://localhost"

def test_semast_resource_invalid_kind_detection():
    """Validates that implementation guards against unsupported resource types."""
    with pytest.raises(ValueError):
        ResourceKind("UNKNOWN_KIND")
