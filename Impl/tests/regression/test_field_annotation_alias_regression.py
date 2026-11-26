import json

import pytest

from Impl.tests.field_annotation_alias_cases import missing_aliases, run_cli, write_design


@pytest.mark.parametrize(("version", "line"), [("1.1", 7), (None, 6)])
def test_legacy_unaliased_fields_continue_to_validate(tmp_path, version, line):
    """Validation/Regression/field_annotation_alias_regression.gasd, scenario 1."""
    source = write_design(tmp_path / "legacy.gasd", version=version)
    result = run_cli(tmp_path, "--json", source)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["semantic_validate"]["status"] == "PASSED"
    assert missing_aliases(json.loads(result.stderr)["reports"][0]) == [("INFO", line, 17)]


def test_lint_severity_comes_from_each_field_annotations_file(tmp_path):
    """Validation/Regression/field_annotation_alias_regression.gasd, scenario 2."""
    legacy = write_design(tmp_path / "legacy.gasd", version="1.1", namespace="example.legacy")
    strict = write_design(tmp_path / "strict.gasd")
    result = run_cli(tmp_path, "--json", "--ast-combine", legacy, strict)

    assert result.returncode == 1, result.stderr
    assert result.stdout == ""
    reports = {report["sourceFile"]: missing_aliases(report) for report in json.loads(result.stderr)["reports"]}
    assert reports == {legacy: [("INFO", 7, 17)], strict: [("ERROR", 7, 17)]}
