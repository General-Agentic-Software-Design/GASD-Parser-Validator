import pytest
from Impl.semantic.DirectiveResolver import DirectiveResolver
from Impl.semantic.SymbolTable import SemanticError

def test_semast_directive_resolution():
    resolver = DirectiveResolver()
    
    directives = [
        {"kind": "CONTEXT", "value": "Compiler Design"},
        {"kind": "TARGET", "value": "TypeScript, Python"}
    ]
    
    # ENSURE "System metadata accurately reflects directive values"
    metadata = resolver.resolve(directives)
    assert metadata.context == "Compiler Design"
    assert metadata.target == ["TypeScript", "Python"]


def test_semast_trace_gathering():
    resolver = DirectiveResolver()
    
    directives = [
        {"kind": "TRACE", "value": "US-001"}
    ]
    resolver.resolve(directives)
    resolver.add_inline_traces(["AC-001", "AC-002"])
    
    # ENSURE "System-wide traces list aggregates all values accurately"
    metadata = resolver.resolve([])
    assert "US-001" in metadata.trace
    assert "AC-001" in metadata.trace
    assert "AC-002" in metadata.trace


def test_semast_global_constraint():
    resolver = DirectiveResolver()
    
    directives = [
        {"kind": "CONTEXT", "value": "Nested Context", "scope": "Local"}
    ]
    
    # ENSURE "Parser rejects non-global directive placement"
    with pytest.raises(SemanticError, match="InvalidScope"):
        resolver.resolve(directives)


def test_semast_trace_format():
    resolver = DirectiveResolver()
    
    # ENSURE "Resolver rejects non-alphanumeric/hyphenated sequence"
    with pytest.raises(SemanticError, match="InvalidTraceFormat"):
        resolver.verify_trace_ids(["US!001@"])


def test_semast_directive_regression_duplicate():
    resolver = DirectiveResolver()
    
    directives = [
        {"kind": "CONTEXT", "value": "Context 1"},
        {"kind": "CONTEXT", "value": "Context 2"}
    ]
    
    # ENSURE "Resolver either merges or warns based on semantic policy"
    metadata = resolver.resolve(directives)
    assert metadata.context == "Context 1 | Context 2"
