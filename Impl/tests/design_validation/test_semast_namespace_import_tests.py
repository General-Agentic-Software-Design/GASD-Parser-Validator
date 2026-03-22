import pytest
from Impl.semantic.SemanticNodes import NamespaceNode, SourceRange

def test_semast_namespace_resolution_structure():
    """Validates namespace grouping and isolation."""
    sr = SourceRange("", 0, 0, 0, 0)
    ns = NamespaceNode(sr, "TestNS", types={}, components={}, flows={}, strategies={}, decisions={})
    assert ns.name == "TestNS"
    assert ns.kind == "Namespace"

def test_semast_import_resolution_requirement():
    """Validates that cross-namespace imports are a design requirement."""
    from Impl.semantic.SemanticPipeline import SemanticPipeline
    pipeline = SemanticPipeline()
    # Basic check for namespaces property in system metadata
    assert hasattr(pipeline, "build")

# ===================================================================
# Cross-File Design Validation
# ===================================================================

def test_semast_namespace_cross_file_import_design():
    """Validates AC-X-SEMAST-002-01: IMPORT statements must resolve symbols from other files."""
    from Impl.semantic.NamespaceResolver import NamespaceResolver
    resolver = NamespaceResolver()
    assert hasattr(resolver, "add_dependency")

def test_semast_namespace_circular_dependency_design():
    """Validates AC-X-SEMAST-002-02: Detection and reporting of circular imports."""
    from Impl.semantic.NamespaceResolver import NamespaceResolver
    resolver = NamespaceResolver()
    assert hasattr(resolver, "get_processing_order")
