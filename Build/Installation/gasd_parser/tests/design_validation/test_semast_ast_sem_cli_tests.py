import pytest

def test_semast_cli_activation():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_activation as source_test_semast_cli_activation
    source_test_semast_cli_activation()

def test_semast_cli_dual_output():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_dual_output as source_test_semast_cli_dual_output
    source_test_semast_cli_dual_output()

def test_semast_cli_output_dir():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_output_dir as source_test_semast_cli_output_dir
    source_test_semast_cli_output_dir()

def test_semast_cli_combine():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_combine as source_test_semast_cli_combine
    source_test_semast_cli_combine()

def test_semast_cli_errors():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_errors as source_test_semast_cli_errors
    source_test_semast_cli_errors()

def test_semast_cli_default_behavior():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_default_behavior as source_test_semast_cli_default_behavior
    source_test_semast_cli_default_behavior()

def test_semast_cli_combined_opts():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_combined_opts as source_test_semast_cli_combined_opts
    source_test_semast_cli_combined_opts()

def test_semast_cli_regression_missing_file():
    from Impl.tests.acceptance.test_semast_cli import test_semast_cli_regression_missing_file as source_test_semast_cli_regression_missing_file
    source_test_semast_cli_regression_missing_file()

