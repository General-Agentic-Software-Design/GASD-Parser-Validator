import pytest
from Impl.semantic.SemanticNodes import (
    SemanticNodeBase, SourceRange, TypeContract, SemanticSystem, NamespaceNode, SystemMetadata
)

def test_semast_model_core_generation():
    """Validates core semantic model generation requirements."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    node = SemanticNodeBase("ResolvedType", sr)
    assert node.kind == "ResolvedType"
    assert node.hash is not None

def test_semast_root_system_structure():
    """Validates the structure of the root SemanticSystem."""
    metadata = SystemMetadata("C", ["T"], ["Tr"])
    system = SemanticSystem(namespaces={}, global_constraints=[], metadata=metadata)
    assert system.kind == "SemanticSystem"
    assert system.metadata.context == "C"

def test_semast_type_contract_recursive():
    """Validates recursive type contracts are correctly modelable."""
    inner = TypeContract("String")
    outer = TypeContract("List", args=[inner])
    assert outer.baseType == "List"
    assert outer.args[0].baseType == "String"

def test_semast_deterministic_hash_consistency():
    """Validates that hashing is stable across instances."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    n1 = SemanticNodeBase("T", sr)
    n2 = SemanticNodeBase("T", sr)
    assert n1.hash == n2.hash
