import pytest
from Impl.semantic.LintEngine import LintEngine
from Impl.semantic.SemanticNodes import ResolvedComponentNode, ResolvedAnnotation, ScopeEnum, SourceRange
from Impl.semantic.SemanticErrorReporter import SemanticErrorReporter

def test_lint_engine_trace_format_v12():
    reporter = SemanticErrorReporter()
    reporter.errors.clear()
    engine = LintEngine(reporter=reporter, version="1.2")
    
    # Create a mock node with a bad trace annotation
    bad_ann = ResolvedAnnotation(name="trace", scope=ScopeEnum.COMPONENT, arguments={"value": "INVALID_ID!"})
    dummy_range = SourceRange("test.gasd", 1, 1, 1, 1)
    node = ResolvedComponentNode(dummy_range, "MyComp", "", [], [], {})
    node.annotations = [bad_ann]
    
    engine.lint_node(node)
    
    # In 1.2, it expects both Trace ID error (LINT-001) and Mandatory AS error (LINT-002)
    assert len(reporter.errors) == 2
    assert reporter.errors[0].message == "Trace identifier 'INVALID_ID!' must be alphanumeric with hyphens."
    assert reporter.errors[1].message == "Annotation @trace is missing mandatory 'AS' identifier in GASD 1.2"

def test_lint_engine_trace_format_v11():
    reporter = SemanticErrorReporter()
    reporter.errors.clear()
    engine = LintEngine(reporter=reporter, version="1.1")
    
    # Create the same bad trace annotation
    bad_ann = ResolvedAnnotation(name="trace", scope=ScopeEnum.COMPONENT, arguments={"value": "INVALID_ID!"})
    dummy_range = SourceRange("test.gasd", 1, 1, 1, 1)
    node = ResolvedComponentNode(dummy_range, "MyComp", "", [], [], {})
    node.annotations = [bad_ann]

    engine.lint_node(node)
    
    # In 1.1, trace format wasn't strictly enforced, so it remains a warning or might not be tested as strictly,
    # but based on our implementation, it warns anyway. BUT it DOES NOT warn about mandatory AS, because that's 1.2 only
    # In 1.1, trace format warns, and missing AS is now an INFO hint
    assert len(reporter.errors) == 2
    assert reporter.errors[0].message == "Trace identifier 'INVALID_ID!' must be alphanumeric with hyphens."
    assert reporter.errors[1].level.value == "INFO"

