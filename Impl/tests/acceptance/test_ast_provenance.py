"""Executable acceptance, regression, negative and design checks for AST provenance."""

from copy import deepcopy
from hashlib import sha512
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
BYTE_HASH = "semantic_ast_bytes_sha512"
CONTENT_HASH = "semantic_ast_content_sha512"
RULES_VERSION = "semantic_ast_content_version"


def spec(namespace, declaration, version="1.1"):
    return (f'VERSION {version}\nCONTEXT: "Provenance"\nTARGET: "Python"\n'
            f'NAMESPACE: "{namespace}"\n{declaration}\n').encode("utf-8")


def run_cli(directory, *args, stdin=None):
    return subprocess.run(
        [sys.executable, "-m", "Impl.cli", "--json", *map(str, args)],
        cwd=directory, env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True, input=stdin,
    )


def export(directory, *args, stdin=None, destination=None):
    options = ["--ast-output", destination] if destination else []
    result = run_cli(directory, *options, *args, stdin=stdin)
    assert result.returncode == 0, result.stderr.decode()
    if destination:
        assert result.stdout == b""
        artifact = (directory / destination).read_bytes()
    else:
        artifact = result.stdout
    marker = json.loads(result.stderr)["semantic_validate"]
    assert marker[BYTE_HASH] == sha512(artifact).hexdigest()
    assert marker[RULES_VERSION] == "1"
    assert len(marker[CONTENT_HASH]) == 128
    assert set(marker[CONTENT_HASH]) <= set("0123456789abcdef")
    return artifact, marker


def assert_sources(artifact, expected):
    assert json.loads(artifact)["provenance"]["sources"] == [
        {"path": name, "sha512": sha512(data).hexdigest()}
        for name, data in sorted(expected.items())
    ]


def assert_no_fingerprints(result):
    marker = json.loads(result.stderr).get("semantic_validate", {})
    assert {BYTE_HASH, CONTENT_HASH, RULES_VERSION}.isdisjoint(marker)


def test_import_inventory_and_edits(tmp_path):
    """AT-AST-PROVENANCE-014-01 and AT-AST-PROVENANCE-014-02."""
    entry = spec("app", 'IMPORT "dep.gasd" AS Dep\nTYPE Item: value: Dep.Value')
    dependency = spec("dependency", 'TYPE Value: text: String').replace(b"\n", b"\r\n")
    (tmp_path / "entry.gasd").write_bytes(entry)
    (tmp_path / "dep.gasd").write_bytes(dependency)
    (tmp_path / "unrelated.gasd").write_bytes(spec("other", 'TYPE Other: id: Integer'))

    artifact, _ = export(tmp_path, "entry.gasd")
    assert_sources(artifact, {"entry.gasd": entry, "dep.gasd": dependency})
    model = json.loads(artifact)
    assert model["namespaces"]["app"]["types"]["Item"]["sourceMap"]["file"] == "entry.gasd"
    assert model["namespaces"]["dependency"]["types"]["Value"]["sourceMap"]["file"] == "dep.gasd"

    changed_entry = entry.replace(b"TYPE Item", b"TYPE Renamed")
    (tmp_path / "entry.gasd").write_bytes(changed_entry)
    artifact, _ = export(tmp_path, "entry.gasd")
    assert_sources(artifact, {"entry.gasd": changed_entry, "dep.gasd": dependency})

    changed_dependency = dependency.replace(b"String", b"Integer")
    (tmp_path / "dep.gasd").write_bytes(changed_dependency)
    artifact, _ = export(tmp_path, "entry.gasd")
    assert_sources(artifact, {"entry.gasd": changed_entry, "dep.gasd": changed_dependency})


def test_standalone_shared_and_transitive_sources(tmp_path):
    """AT-AST-PROVENANCE-014-04."""
    sources = {
        "x.gasd": spec("x", 'IMPORT "shared.gasd" AS Shared\nTYPE X: data: Shared.Common'),
        "y.gasd": spec("y", 'IMPORT "shared.gasd" AS Shared\nTYPE Y: data: Shared.Common'),
        "shared.gasd": spec("shared", 'IMPORT "leaf.gasd" AS Leaf\nTYPE Common: data: Leaf.Data'),
        "leaf.gasd": spec("leaf", 'TYPE Data: text: String'),
    }
    for name, data in sources.items():
        (tmp_path / name).write_bytes(data)
    assert_sources(export(tmp_path, "leaf.gasd")[0], {"leaf.gasd": sources["leaf.gasd"]})
    assert_sources(export(tmp_path, "y.gasd", "x.gasd")[0], sources)


@pytest.mark.parametrize("source_name", ["entry.gasd", "dep.gasd"])
def test_bytes_captured_before_parse(tmp_path, monkeypatch, capsysbinary, source_name):
    """RT-AST-PROVENANCE-014-01."""
    from Impl import cli
    from Impl.parser.ParseTreeAPI import ParseTreeAPI

    entry = spec("app", 'IMPORT "dep.gasd" AS Dep\nTYPE Item: original: String')
    dep = spec("dep", 'TYPE Value: original: String')
    (tmp_path / "entry.gasd").write_bytes(entry)
    (tmp_path / "dep.gasd").write_bytes(dep)
    parse = ParseTreeAPI.parse

    def change_disk_version(self, source, source_file="<string>"):
        if Path(source_file).name == source_name:
            path = tmp_path / source_name
            path.write_bytes(path.read_bytes().replace(b"original", b"replacement"))
        return parse(self, source, source_file)

    monkeypatch.setattr(ParseTreeAPI, "parse", change_disk_version)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", "entry.gasd"])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    result = capsysbinary.readouterr()
    assert stopped.value.code == 0, result.err.decode()
    assert b"replacement" in (tmp_path / source_name).read_bytes()
    assert b'"original"' in result.out and b'"replacement"' not in result.out
    assert_sources(result.out, {"entry.gasd": entry, "dep.gasd": dep})


def test_raw_stdin_inventory(tmp_path):
    """RT-AST-PROVENANCE-014-02."""
    source = spec("app", 'TYPE Item: value: String', version="1.2").replace(b"\n", b"\r\n")
    assert_sources(export(tmp_path, "-", stdin=source)[0], {"stdin": source})


@pytest.mark.parametrize("version", ["1.1", "1.2"])
def test_report_matches_both_export_destinations(tmp_path, version):
    """AT-AST-PROVENANCE-015-01 and AT-AST-PROVENANCE-015-03."""
    (tmp_path / "entry.gasd").write_bytes(spec("app", 'TYPE Item: value: String', version))
    stdout, stdout_report = export(tmp_path, "entry.gasd")
    artifact, file_report = export(tmp_path, "entry.gasd", destination="ast.json")
    assert ("semantic_validate" in json.loads(stdout)) is (version == "1.2")
    assert stdout_report[CONTENT_HASH] == file_report[CONTENT_HASH]
    for consumer in ("pox", "scaffgen"):
        delivered = tmp_path / f"{consumer}.json"
        delivered.write_bytes(artifact)
        assert delivered.read_bytes() == artifact
        assert sha512(delivered.read_bytes()).hexdigest() == file_report[BYTE_HASH]


@pytest.mark.parametrize("destination", [None, "ast.json"])
def test_embedded_fingerprints(tmp_path, destination):
    """RT-AST-PROVENANCE-015-03: Verify the AST marker against the delivered bytes."""
    source = spec("app", 'TYPE Item: value: String', version="1.2")
    (tmp_path / "entry.gasd").write_bytes(source)
    artifact, report_marker = export(tmp_path, "entry.gasd", destination=destination)
    marker = json.loads(artifact)["semantic_validate"]

    embedded_digest = marker[BYTE_HASH]
    assert len(embedded_digest) == 128
    assert set(embedded_digest) <= set("0123456789abcdef")
    digest_field = f'"{BYTE_HASH}": "{embedded_digest}"'.encode("ascii")
    assert artifact.count(digest_field) == 1
    zeroed_field = digest_field.replace(embedded_digest.encode("ascii"), b"0" * 128)
    zeroed_artifact = artifact.replace(digest_field, zeroed_field, 1)
    assert embedded_digest == sha512(zeroed_artifact).hexdigest()
    assert {**marker, BYTE_HASH: sha512(artifact).hexdigest()} == report_marker


@pytest.mark.parametrize("name", ["entry.gasd", "dep.gasd"])
@pytest.mark.parametrize("failure", ["read", "identify"])
def test_required_source_failure(tmp_path, monkeypatch, capsysbinary, name, failure):
    """AT-AST-PROVENANCE-014-03."""
    from Impl import cli
    from Impl.semantic.SemanticASTExporter import SemanticASTExporter

    (tmp_path / "entry.gasd").write_bytes(spec("app", 'IMPORT "dep.gasd"\nTYPE Item: value: String'))
    (tmp_path / "dep.gasd").write_bytes(spec("dep", 'TYPE Value: value: String'))
    if failure == "read":
        read_bytes = Path.read_bytes

        def read_file(path):
            if path.name == name:
                raise PermissionError("fixture source cannot be read")
            return read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", read_file)
    else:
        relativize = SemanticASTExporter._do_relativize

        def logical_path(self, path, cwd):
            if Path(path).name == name:
                raise ValueError("fixture source cannot be identified")
            return relativize(self, path, cwd)

        monkeypatch.setattr(SemanticASTExporter, "_do_relativize", logical_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", "entry.gasd"])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    output = capsysbinary.readouterr()
    assert stopped.value.code != 0
    assert output.out == b""
    assert name.encode() in output.err
    assert_no_fingerprints(subprocess.CompletedProcess([], stopped.value.code, output.out, output.err))


def test_missing_transitive_import_fails_export(tmp_path):
    """AT-AST-PROVENANCE-014-03 covers a required unresolved file."""
    (tmp_path / "entry.gasd").write_bytes(spec("app", 'IMPORT "dep.gasd"\nTYPE Item: value: String'))
    (tmp_path / "dep.gasd").write_bytes(spec("dep", 'IMPORT "missing.gasd"\nTYPE Value: value: String'))
    result = run_cli(tmp_path, "entry.gasd")
    assert result.returncode != 0
    assert result.stdout == b""
    assert b"missing.gasd" in result.stderr
    assert_no_fingerprints(result)


def test_failure_reports_do_not_fingerprint(tmp_path):
    """AT-AST-PROVENANCE-015-02."""
    source = tmp_path / "entry.gasd"
    source.write_bytes(spec("app", 'TYPE Item: value: String', version="1.2"))
    old, _ = export(tmp_path, "entry.gasd", destination="ast.json")
    syntax = run_cli(tmp_path, "--no-validate", "entry.gasd")
    assert syntax.returncode == 0 and syntax.stdout
    assert_no_fingerprints(syntax)
    (tmp_path / "blocked.json").mkdir()
    failed_write = run_cli(tmp_path, "--ast-output", "blocked.json", "entry.gasd")
    assert failed_write.returncode != 0
    assert json.loads(failed_write.stderr)["success"] is False
    assert_no_fingerprints(failed_write)
    source.write_bytes(spec("app", 'TYPE Item: value: UnknownType', version="1.2"))
    failed_validation = run_cli(tmp_path, "--ast-output", "ast.json", "entry.gasd")
    assert failed_validation.returncode != 0
    assert_no_fingerprints(failed_validation)
    assert (tmp_path / "ast.json").read_bytes() == old


def test_terminal_newline_is_hashed(tmp_path, monkeypatch, capsysbinary):
    """RT-AST-PROVENANCE-015-01."""
    from Impl import cli
    from Impl.semantic.SemanticASTExporter import SemanticASTExporter

    (tmp_path / "entry.gasd").write_bytes(spec("app", 'TYPE Item: value: String'))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", "entry.gasd"])
    serializer = SemanticASTExporter.to_json
    artifact = None

    def with_optional_newline(self, *args, **kwargs):
        nonlocal artifact
        if artifact is None:
            artifact = serializer(self, *args, **kwargs)
            return artifact
        return artifact + "\n"

    monkeypatch.setattr(SemanticASTExporter, "to_json", with_optional_newline)
    outputs = []
    for _ in range(2):
        with pytest.raises(SystemExit) as stopped:
            cli.main()
        assert stopped.value.code == 0
        out, err = capsysbinary.readouterr()
        marker = json.loads(err)["semantic_validate"]
        assert marker[BYTE_HASH] == sha512(out).hexdigest()
        outputs.append((out, marker))
    assert outputs[1][0] == outputs[0][0] + b"\n"
    assert outputs[1][1][CONTENT_HASH] == outputs[0][1][CONTENT_HASH]
    assert outputs[1][1][BYTE_HASH] != outputs[0][1][BYTE_HASH]


def test_content_changes_and_comment_stability(tmp_path):
    """AT-AST-PROVENANCE-017-02 and RT-AST-PROVENANCE-017-02."""
    path = tmp_path / "entry.gasd"
    source = spec("app", 'TYPE Item: value: String', version="1.2")
    path.write_bytes(source)
    original_ast, original = export(tmp_path, path.name)
    path.write_bytes(source.replace(b'TYPE Item', b'// Different comment\nTYPE Item'))
    commented_ast, comment = export(tmp_path, path.name)
    assert json.loads(original_ast)["provenance"] != json.loads(commented_ast)["provenance"]
    assert original[CONTENT_HASH] == comment[CONTENT_HASH]
    assert original[BYTE_HASH] != comment[BYTE_HASH]
    path.write_bytes(source.replace(b"String", b"Integer"))
    _, changed = export(tmp_path, path.name)
    assert changed[CONTENT_HASH] != original[CONTENT_HASH]
    assert changed[BYTE_HASH] != original[BYTE_HASH]


def test_content_collection_order(tmp_path):
    """RT-AST-PROVENANCE-017-03."""
    path = tmp_path / "entry.gasd"
    constraints = ['CONSTRAINT: "alpha"', 'CONSTRAINT: "beta"']

    def write_revision(constraints, first, second):
        flow = (f'FLOW run():\n    1. ACHIEVE "{first}"\n        POSTCONDITION: "Done"\n'
                f'    2. ACHIEVE "{second}"\n        POSTCONDITION: "Done"')
        path.write_bytes(spec("app", "\n".join([*constraints, flow]), version="1.2"))
        return export(tmp_path, path.name)[1]

    original = write_revision(constraints, "first", "second")
    unordered = write_revision(constraints[::-1], "first", "second")
    reordered = write_revision(constraints, "second", "first")
    assert original[CONTENT_HASH] == unordered[CONTENT_HASH]
    assert original[CONTENT_HASH] != reordered[CONTENT_HASH]
    assert original[BYTE_HASH] != reordered[BYTE_HASH]


def test_canonical_projection_and_generated_references():
    """AT-AST-PROVENANCE-017-01, RT-AST-PROVENANCE-017-01 and RT-AST-PROVENANCE-017-04."""
    from Impl.semantic.ASTProvenance import canonical_content

    arguments = {"id": "authored", "sourceMap": "literal", "symbolId": "id-a", "label": "café"}
    model = {
        "kind": "SemanticSystem", "id": "id-root", "sourceMap": {"file": "entry.gasd"},
        "provenance": {"sources": []}, "semantic_validate": {"validation_time": "t1"},
        "metadata": {"trace": ["Z", "A"], "files": ["entry.gasd"]},
        "compilationUnit": {"fileNodes": {
            "entry.gasd": {"namespace": "app", "imports": [{"path": "dep.gasd", "alias": "Dep"}]},
            "dep.gasd": {"namespace": "dep", "imports": []},
        }},
        "namespaces": {"app": {
            "types": {
                "A": {"kind": "ResolvedType", "id": "id-a", "sourceMap": {}, "name": "A"},
                "B": {"kind": "ResolvedType", "id": "id-b", "sourceMap": {}, "name": "B"},
            },
            "components": {"C": {"kind": "ResolvedComponent", "id": "id-c", "sourceMap": {},
                                  "dependencies": [{"symbolId": "id-a"}]}},
        }},
        "annotations": [{"name": "metadata", "arguments": arguments}],
        "contracts": [{"kind": "ResolvedContract", "id": "id-contract", "sourceMap": {},
                       "name": "C.run", "hash": "derived", "cases": [
            {"kind": "ContractCase", "name": "z", "sourceFile": "entry.gasd", "line": 12},
            {"kind": "ContractCase", "name": "a", "sourceFile": "entry.gasd", "line": 14},
        ]}],
    }
    expected = {
        "kind": "SemanticSystem", "metadata": {"trace": ["A", "Z"]},
        "imports": [{"namespace": "app", "target": {"namespace": "dep"}, "alias": "Dep"}],
        "namespaces": {"app": {
            "types": {"A": {"kind": "ResolvedType", "name": "A"},
                      "B": {"kind": "ResolvedType", "name": "B"}},
            "components": {"C": {"kind": "ResolvedComponent", "dependencies": [
                {"symbolId": {"node": ["namespaces", "app", "types", "A"]}},
            ]}},
        }},
        "annotations": [{"name": "metadata", "arguments": arguments}],
        "contracts": [{"kind": "ResolvedContract", "name": "C.run", "cases": [
            {"kind": "ContractCase", "name": "z"}, {"kind": "ContractCase", "name": "a"},
        ]}],
    }

    def encode(reference):
        return json.dumps(reference, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def artifact_hash(document):
        return sha512(encode(document)).hexdigest()

    assert canonical_content(model) == encode(expected)
    changed_timestamp = deepcopy(model)
    changed_timestamp["semantic_validate"]["validation_time"] = "t2"
    assert canonical_content(changed_timestamp) == encode(expected)
    assert artifact_hash(changed_timestamp) != artifact_hash(model)
    remapped = deepcopy(model)
    remapped["namespaces"]["app"]["types"]["A"]["id"] = "alternative-a"
    remapped["namespaces"]["app"]["components"]["C"]["dependencies"][0]["symbolId"] = "alternative-a"
    assert canonical_content(remapped) == encode(expected)
    assert artifact_hash(remapped) != artifact_hash(model)
    remapped["namespaces"]["app"]["components"]["C"]["dependencies"][0]["symbolId"] = "id-b"
    expected["namespaces"]["app"]["components"]["C"]["dependencies"][0]["symbolId"]["node"][-1] = "B"
    assert canonical_content(remapped) == encode(expected)
    assert canonical_content(remapped) != canonical_content(model)
