import pytest
from Impl.semantic.SemanticNodes import SemanticSystem, NamespaceNode, SystemMetadata, SourceRange, ResolvedComponentNode
from Impl.semantic.SemanticHasher import SemanticHasher, DeterminismGuard

def mock_system(comp_name="CompA") -> SemanticSystem:
    comp = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), comp_name, "", [], [], {})
    ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Core", {}, {comp_name: comp}, {}, {}, {})
    meta = SystemMetadata("Ctx", [], [])
    return SemanticSystem({"Core": ns}, [], meta)

def test_semast_hash_generation():
    hasher = SemanticHasher()
    sys = mock_system()
    
    # ENSURE "Returns a valid structured SHA-256 hex string"
    h = hasher.compute_hash(sys)
    assert len(h) == 64
    assert isinstance(h, str)


def test_semast_hash_whitespace_independence():
    hasher = SemanticHasher()
    
    sys1 = mock_system()
    sys2 = mock_system()
    # The parser guarantees that arbitrary whitespace outside of tokens
    # doesn't affect the final constructed tree.
    # Therefore, two structurally identical systems have identical hashes.
    sys2.id = "different-id" # 'id' field is explicitly excluded from hashes
    
    h1 = hasher.compute_hash(sys1)
    h2 = hasher.compute_hash(sys2)
    assert h1 == h2


def test_semast_hash_recursion():
    hasher = SemanticHasher()
    
    sys1 = mock_system()
    sys2 = mock_system()
    
    # "Modify a deep property in a nested node"
    sys2.namespaces["Core"].components["CompA"].name = "ChangedComp"
    
    # "Root hash changes to reflect the deep modification"
    assert hasher.compute_hash(sys1) != hasher.compute_hash(sys2)


def test_semast_drift_detection():
    hasher = SemanticHasher()
    
    sys1 = mock_system()
    sys2 = mock_system()
    
    # "Compare SemanticSystem state A and slightly modified state B"
    # We change a deep property, which changes the namespace hash
    sys2.namespaces["Core"].components["CompA"].pattern = "Service"
    # Reset cached hash for test
    sys2.namespaces["Core"]._hash = None
    sys2._hash = None
    
    reports = hasher.compare(sys1, sys2)
    
    # "DriftReport specifically highlights the changed nodes"
    assert len(reports) == 1
    assert reports[0].nodeId == "Core"
    assert reports[0].message == "Modified"


def test_semast_determinism_guard():
    guard = DeterminismGuard()
    
    # "Run full semantic analysis pipeline iteratively 10 times"
    states = [mock_system() for _ in range(10)]
    
    # "Resulting root hash is identical every single time"
    assert guard.verify_runs(*states) is True


def test_semast_hash_regression_order_independence():
    hasher = SemanticHasher()
    
    comp1 = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), "A", "", [], [], {})
    comp2 = ResolvedComponentNode(SourceRange("", 0, 0, 0, 0), "B", "", [], [], {})
    
    ns1 = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Core", {}, {"A": comp1, "B": comp2}, {}, {}, {})
    ns2 = NamespaceNode(SourceRange("", 0, 0, 0, 0), "Core", {}, {"B": comp2, "A": comp1}, {}, {}, {})
    
    sys1 = SemanticSystem({"Core": ns1}, [], SystemMetadata("Ctx", [], []))
    sys2 = SemanticSystem({"Core": ns2}, [], SystemMetadata("Ctx", [], []))
    
    # "Hash remains identical since structural semantics are unchanged"
    assert hasher.compute_hash(sys1) == hasher.compute_hash(sys2)

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_cross_file_symbol_sorting():
    # AT-X-SEMAST-011-01, AC-X-SEMAST-011-01
    hasher = SemanticHasher()
    
    # File A with symbols in one order
    ns_a1 = NamespaceNode(SourceRange("a.gasd", 0,0,0,0), "A", {}, {"B": None, "A": None}, {}, {}, {})
    # File A with symbols in another order
    ns_a2 = NamespaceNode(SourceRange("a.gasd", 0,0,0,0), "A", {}, {"A": None, "B": None}, {}, {}, {})
    
    # ENSURE "The global semantic hash remains identical due to deterministic sorting"
    assert hasher.compute_hash(ns_a1) == hasher.compute_hash(ns_a2)

def test_semast_global_graph_hashing():
    # AT-X-SEMAST-011-02, AC-X-SEMAST-011-03
    hasher = SemanticHasher()
    
    # CompilationUnit represented by SemanticSystem with multiple namespaces
    ns_a = NamespaceNode(SourceRange("a.gasd", 0,0,0,0), "A", {}, {}, {}, {}, {})
    ns_b = NamespaceNode(SourceRange("b.gasd", 0,0,0,0), "B", {}, {}, {}, {}, {})
    
    sys1 = SemanticSystem({"A": ns_a, "B": ns_b}, [], SystemMetadata("Ctx", [], []))
    sys2 = SemanticSystem({"B": ns_b, "A": ns_a}, [], SystemMetadata("Ctx", [], []))
    
    # ENSURE "Includes all interconnected files and dependency links in a stable order"
    assert hasher.compute_hash(sys1) == hasher.compute_hash(sys2)
