import json

import pytest

from Impl.tests.field_annotation_alias_cases import missing_aliases, run_cli, write_design


@pytest.mark.parametrize("output_flags", [(), ("--ast-output", "ast.json")], ids=["stdout", "file"])
def test_missing_field_annotation_alias_blocks_ast_export(tmp_path, output_flags):
    """Validation/Negative/field_annotation_alias_negative.gasd, scenario 1."""
    source = write_design(tmp_path / "hello.gasd")
    result = run_cli(tmp_path, "--json", "--ast-combine", *output_flags, source)

    assert result.returncode == 1, result.stderr
    assert result.stdout == ""
    assert not (tmp_path / "ast.json").exists()
    report = json.loads(result.stderr)
    assert report["semantic_validate"]["status"] == "FAILED"
    assert missing_aliases(report["reports"][0]) == [("ERROR", 7, 17)]


def test_diagnoses_each_unaliased_annotation_on_the_field(tmp_path):
    """Validation/Negative/field_annotation_alias_negative.gasd, scenario 2."""
    source = write_design(tmp_path / "hello.gasd", "@min_length(1) @max_length(20)")
    result = run_cli(tmp_path, "--json", source)

    assert result.returncode == 1, result.stderr
    assert missing_aliases(json.loads(result.stderr)["reports"][0]) == [("ERROR", 7, 17), ("ERROR", 7, 32)]
