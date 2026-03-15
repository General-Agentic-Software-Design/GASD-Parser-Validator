import pytest

def test_semast_directive_resolution():
    from Impl.tests.acceptance.test_semast_directives import test_semast_directive_resolution as source_test_semast_directive_resolution
    source_test_semast_directive_resolution()

def test_semast_trace_gathering():
    from Impl.tests.acceptance.test_semast_directives import test_semast_trace_gathering as source_test_semast_trace_gathering
    source_test_semast_trace_gathering()

def test_semast_global_constraint():
    from Impl.tests.acceptance.test_semast_directives import test_semast_global_constraint as source_test_semast_global_constraint
    source_test_semast_global_constraint()

def test_semast_trace_format():
    from Impl.tests.acceptance.test_semast_directives import test_semast_trace_format as source_test_semast_trace_format
    source_test_semast_trace_format()

def test_semast_directive_regression_duplicate():
    from Impl.tests.acceptance.test_semast_directives import test_semast_directive_regression_duplicate as source_test_semast_directive_regression_duplicate
    source_test_semast_directive_regression_duplicate()

