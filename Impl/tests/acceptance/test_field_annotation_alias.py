import json

from Impl.tests.field_annotation_alias_cases import run_cli, write_design


def test_field_annotation_identifiers_survive_semantic_export(tmp_path):
    """Validation/Acceptance/field_annotation_alias_acceptance.gasd."""
    source = write_design(tmp_path / "hello.gasd", "@min_length(1) AS NAME_MIN @max_length(20) AS NAME_MAX")
    result = run_cli(tmp_path, "--json", "--ast-output", "ast.json", source)

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    ast = json.loads((tmp_path / "ast.json").read_bytes())
    assert ast["semantic_validate"]["status"] == "PASSED"
    field = ast["namespaces"]["example.hello"]["types"]["HelloInput"]["fields"]["name"]
    occurrences = [item for item in ast["source_inventory"] if item["kind"] == "annotation"]
    assert [annotation["alias"] for annotation in field["annotations"]] == ["NAME_MIN", "NAME_MAX"]
    assert [item["alias"] for item in occurrences] == ["NAME_MIN", "NAME_MAX"]
    assert [item["pointer"] for item in occurrences] == [
        f"/namespaces/example.hello/types/HelloInput/fields/name/annotations/{index}" for index in range(2)
    ]
