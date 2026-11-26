import json

from Impl.tests.field_annotation_alias_cases import missing_aliases, run_cli, write_design


def test_validate_field_annotation_without_export(tmp_path):
    """Validation/Design/field_annotation_alias_tests.gasd, scenario 1."""
    source = write_design(tmp_path / "hello.gasd")
    result = run_cli(tmp_path, source)

    assert result.returncode == 1
    assert "LINT-011" in result.stderr
    assert "hello.gasd:7:17" in result.stderr


def test_field_annotation_alias_is_optional_in_syntax_only_mode(tmp_path):
    """Validation/Design/field_annotation_alias_tests.gasd, scenario 2."""
    source = write_design(tmp_path / "hello.gasd")
    result = run_cli(tmp_path, "--no-validate", "--json", source)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)
    assert missing_aliases(json.loads(result.stderr)["reports"][0]) == []
