import pytest
from Impl.semantic.DirectiveResolver import DirectiveResolver
from Impl.semantic.SymbolTable import SemanticError
from Impl.semantic.SemanticNodes import SystemMetadata

def test_semast_directive_resolution():
    resolver = DirectiveResolver()
    meta = resolver.resolve([
        {"kind": "CONTEXT", "value": "Test", "scope": "Global"},
        {"kind": "TARGET", "value": "Py, JS", "scope": "Global"}
    ])
    assert meta.context == "Test"
    assert "Py" in meta.target and "JS" in meta.target

def test_semast_trace_gathering():
    resolver = DirectiveResolver()
    meta = resolver.resolve([
        {"kind": "TRACE", "value": "REQ-123", "scope": "Global"},
        {"kind": "TRACE", "value": "REQ-456", "scope": "Global"}
    ])
    assert "REQ-123" in meta.trace
    assert "REQ-456" in meta.trace

def test_semast_global_constraint():
    resolver = DirectiveResolver()
    with pytest.raises(SemanticError, match="InvalidScope"):
        resolver.resolve([{"kind": "CONTEXT", "value": "X", "scope": "Local"}])

def test_semast_trace_format():
    resolver = DirectiveResolver()
    with pytest.raises(SemanticError, match="InvalidTraceFormat"):
        resolver.resolve([{"kind": "TRACE", "value": "Invalid Format!", "scope": "Global"}])

def test_semast_directive_regression_duplicate():
    resolver = DirectiveResolver()
    meta = resolver.resolve([
        {"kind": "CONTEXT", "value": "Test1", "scope": "Global"},
        {"kind": "CONTEXT", "value": "Test2", "scope": "Global"}
    ])
    assert meta.context == "Test1 | Test2"
