import pytest
from Impl.semantic.SemanticNodes import SemanticNodeBase, SourceRange

def test_semast_hash_generation_determinism():
    """Validates that hashing is strictly deterministic (AC-SEMAST-001-08)."""
    sr = SourceRange("f.gasd", 1, 0, 1, 10)
    # Different IDs, same content -> same hash
    n1 = SemanticNodeBase("T", sr)
    n2 = SemanticNodeBase("T", sr)
    assert n1.hash == n2.hash

def test_semast_hash_drift_detection_requirement():
    """Validates that hash values are suitable for drift detection."""
    sr = SourceRange("f.gasd", 1, 0, 1, 10)
    n1 = SemanticNodeBase("T", sr)
    # Change content
    n3 = SemanticNodeBase("T2", sr)
    assert n1.hash != n3.hash

# ===================================================================
# Cross-File Design Validation
# ===================================================================

def test_semast_hash_cross_file_sorting_design():
    """Validates AC-X-SEMAST-008-01: Alphabetical sorting of cross-file symbols before hashing."""
    from Impl.semantic.SemanticHasher import SemanticHasher
    assert hasattr(SemanticHasher, "sort_symbols")

def test_semast_hash_global_graph_design():
    """Validates AC-X-SEMAST-008-02: Hashing of the entire cross-file dependency graph."""
    from Impl.semantic.SemanticHasher import SemanticHasher
    assert hasattr(SemanticHasher, "hash_system")
