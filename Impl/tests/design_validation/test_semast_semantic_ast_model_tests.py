import pytest
import json
from Impl.semantic.SemanticNodes import (
    SemanticNodeBase, SourceRange, TypeContract, SymbolLink, ResolvedAnnotation, ScopeEnum
)

def test_semast_model_serialization():
    """Validates AC-SEMAST-001-01: Semantic Node Representation & Serialization."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    node = SemanticNodeBase("TestNode", sr)
    d = node.to_dict()
    assert d["kind"] == "TestNode"
    assert "id" in d
    assert "sourceMap" in d
    assert d["sourceMap"]["file"] == "test.gasd"

def test_semast_model_hashing():
    """Validates AC-SEMAST-001-08: Deterministic Hashing."""
    sr = SourceRange("test.gasd", 1, 0, 1, 10)
    node1 = SemanticNodeBase("TestNode", sr)
    node2 = SemanticNodeBase("TestNode", sr)
    # The IDs will be different, but the cleaned hash (which ignores ID) should be the same if content is same.
    assert node1.hash == node2.hash

def test_semast_model_symbol_links():
    """Validates AC-SEMAST-001-09: Weak GUID-based References."""
    link = SymbolLink("guid-123")
    d = link.to_dict()
    assert d["symbolId"] == "guid-123"

def test_semast_model_type_contract():
    """Validates AC-SEMAST-001-03: Type Contract structure."""
    tc = TypeContract("List", args=[TypeContract("String")])
    d = tc.to_dict()
    assert d["baseType"] == "List"
    assert len(d["args"]) == 1
    assert d["args"][0]["baseType"] == "String"
