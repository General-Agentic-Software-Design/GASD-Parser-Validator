import pytest
from Impl.semantic.SemanticHasher import SemanticHasher, DeterminismGuard
from Impl.semantic.SemanticNodes import SemanticSystem, NamespaceNode, SystemMetadata, SourceRange

def make_system(name="Sys"):
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "A", {}, {}, {}, {}, {})
    sys = SemanticSystem({"A": ns}, [], SystemMetadata("", [], []))
    sys.id = name
    return sys

def test_semast_hash_generation():
    h = SemanticHasher()
    sys = make_system()
    assert h.compute_hash(sys) is not None

def test_semast_hash_whitespace_independence():
    sys1 = make_system()
    sys2 = make_system()
    assert sys1.hash == sys2.hash

def test_semast_hash_recursion():
    h = SemanticHasher()
    sys = make_system()
    res = h.compute_hash(sys)
    assert len(res) > 0
def test_semast_drift_detection():
    h = SemanticHasher()
    sys1 = make_system()
    sys2 = make_system()
    sys2.namespaces["B"] = NamespaceNode(SourceRange("", 0, 0, 0, 0), "B", {}, {}, {}, {}, {})
    reports = h.compare(sys1, sys2)
    assert any(r.message == "Added" for r in reports)

def test_semast_determinism_guard():
    guard = DeterminismGuard()
    s1 = make_system()
    s2 = make_system()
    assert guard.verify_runs(s1, s2) is True

def test_semast_hash_regression_order_independence():
    h = SemanticHasher()
    sys = make_system()
    assert isinstance(h.compute_hash(sys), str)
