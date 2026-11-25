"""Executable checks for the four CPC AST validation specifications."""

from hashlib import sha512
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
VERIFIED = 'entry.gasd'


def write_spec(root, relative_path, namespace, body, version="1.1"):
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        f'VERSION {version}\nCONTEXT: "CPC AST"\nTARGET: "Python"\n'
        f'NAMESPACE: "{namespace}"\n{body}\n'.encode()
    )
    return path


def run_cli(root, *arguments):
    return subprocess.run(
        [sys.executable, "-m", "Impl", *map(str, arguments)],
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
    )


def export(root, entry=VERIFIED, destination=None):
    extra = ["--ast-output", destination] if destination is not None else []
    process = run_cli(root, "--json", *extra, entry)
    assert process.returncode == 0, process.stderr.decode()
    report = json.loads(process.stderr)
    assert report["success"] is True
    if destination is None:
        payload = process.stdout
    else:
        assert not process.stdout
        payload = (root / destination).read_bytes()
    assert report["semantic_ast_sha512"] == sha512(payload).hexdigest()
    assert report["semantic_validate"]["semantic_ast_bytes_sha512"] == report["semantic_ast_sha512"]
    return json.loads(payload), payload


def resolve(artifact, pointer):
    item = artifact
    assert pointer.startswith("/")
    for part in pointer[1:].split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        item = item[int(key)] if isinstance(item, list) else item[key]
    return item


@pytest.fixture
def import_chain(tmp_path):
    specs = {
        VERIFIED: ("app", 'IMPORT "imports/direct.gasd" AS Direct\nTYPE Entry: original: Direct.DirectItem'),
        "imports/direct.gasd": (
            "direct", 'IMPORT "nested/leaf.gasd" AS Leaf\nTYPE DirectItem: original: Leaf.LeafItem'
        ),
        "imports/nested/leaf.gasd": ("leaf", "TYPE LeafItem: original: String"),
    }
    for filename, (namespace, body) in specs.items():
        file = write_spec(tmp_path, filename, namespace, body)
        if namespace == "leaf":
            file.write_bytes(file.read_bytes().replace(b"\n", b"\r\n"))
    write_spec(tmp_path, "unrelated.gasd", "unused", "TYPE Unused: value: String")
    return {filename: (tmp_path / filename).read_bytes() for filename in specs}


@pytest.mark.parametrize("absolute_entry", [False, True])
def test_cpc_source_inventory(tmp_path, import_chain, absolute_entry):
    """AST-AT-001 and AST-AC-001-02."""
    entry = tmp_path / VERIFIED if absolute_entry else VERIFIED
    artifact, _ = export(tmp_path, entry)
    assert artifact["provenance"]["sources"] == [
        {"path": path, "sha512": sha512(payload).hexdigest()}
        for path, payload in sorted(import_chain.items())
    ]
    for path, namespace, name in zip(import_chain, ("app", "direct", "leaf"), ("Entry", "DirectItem", "LeafItem")):
        assert artifact["namespaces"][namespace]["types"][name]["sourceMap"]["file"] == path


@pytest.mark.parametrize("source_name", [VERIFIED, "imports/direct.gasd", "imports/nested/leaf.gasd"])
def test_cpc_uses_original_capture(tmp_path, import_chain, source_name, monkeypatch, capsysbinary):
    """AST-AT-002 and AST-AC-001-01."""
    from Impl import cli
    from Impl.parser.ParseTreeAPI import ParseTreeAPI

    parse = ParseTreeAPI.parse

    def change_source(self, source, source_file="<string>"):
        path = Path(source_file)
        if path == tmp_path / source_name:
            path.write_bytes(import_chain[source_name].replace(b"original", b"replacement"))
        return parse(self, source, source_file)

    monkeypatch.setattr(ParseTreeAPI, "parse", change_source)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", VERIFIED])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    out, err = capsysbinary.readouterr()
    assert stopped.value.code == 0, err.decode()
    assert b"replacement" in (tmp_path / source_name).read_bytes()
    assert b'"original"' in out and b'"replacement"' not in out
    assert json.loads(out)["provenance"]["sources"] == [
        {"path": path, "sha512": sha512(payload).hexdigest()}
        for path, payload in sorted(import_chain.items())
    ]


@pytest.mark.parametrize("target", [VERIFIED, "imports/direct.gasd"])
def test_cpc_read_failures(tmp_path, import_chain, target, monkeypatch, capsysbinary):
    """AST-AT-002 and AST-AC-001-03."""
    from Impl import cli

    read_bytes = Path.read_bytes

    def unreadable(path):
        if path == tmp_path / target:
            raise PermissionError("fixture denies reading this source")
        return read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", unreadable)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", "--ast-output", "ast.json", VERIFIED])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    out, err = capsysbinary.readouterr()
    assert stopped.value.code != 0 and not out
    report = json.loads(err)
    assert report["success"] is False
    assert target in err.decode()
    assert "semantic_ast_sha512" not in report
    assert not (tmp_path / "ast.json").exists()


@pytest.mark.parametrize("transitive", [False, True])
@pytest.mark.parametrize("missing", ["missing.gasd", "./missing-source"])
def test_cpc_missing_import(tmp_path, transitive, missing):
    """AST-AC-001-03."""
    importer = "direct.gasd" if transitive else VERIFIED
    if transitive:
        write_spec(tmp_path, VERIFIED, "app", 'IMPORT "direct.gasd"\nTYPE Entry: value: String')
    write_spec(tmp_path, importer, "importer", f'IMPORT "{missing}"\nTYPE Item: value: String')
    process = run_cli(tmp_path, "--json", "--ast-output", "ast.json", VERIFIED)
    assert process.returncode != 0 and not process.stdout
    report = json.loads(process.stderr)
    assert report["success"] is False
    errors = [error for item in report["reports"] for error in item["errors"]]
    assert any("missing" in json.dumps(error) and error.get("location", {}).get("line") == 5 for error in errors)
    assert "semantic_ast_sha512" not in report and not (tmp_path / "ast.json").exists()


def test_cpc_conflicting_source_paths(tmp_path, monkeypatch, capsysbinary):
    """AST-AC-001-03."""
    from Impl import cli
    from Impl.semantic.SemanticASTExporter import SemanticASTExporter

    write_spec(tmp_path, VERIFIED, "app", "TYPE Entry: value: String")
    write_spec(tmp_path, "second.gasd", "secondary", "TYPE Other: value: String")
    relativize = SemanticASTExporter._do_relativize

    def duplicate_path(self, path, cwd):
        return VERIFIED if Path(path).name == "second.gasd" else relativize(self, path, cwd)

    monkeypatch.setattr(SemanticASTExporter, "_do_relativize", duplicate_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", VERIFIED, "second.gasd"])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    out, err = capsysbinary.readouterr()
    assert stopped.value.code != 0 and not out
    report = json.loads(err)
    assert report["success"] is False and "semantic_ast_sha512" not in report
    assert "conflict" in err.decode().lower()


@pytest.fixture
def checked_spec(tmp_path):
    body = """TYPE RecordId:
    id: Integer @min(1) AS MIN_ID
COMPONENT Checker:
    INTERFACE:
        read(value: Integer) -> RecordId
CONTRACT Checker.read:
    INPUT: value: Integer
    OUTPUT: RecordId
    BEHAVIORS:
        CASE success:
            WHEN: value > 0
            POSTCONDITION: result.id IS Integer
FLOW validate(value: Integer) -> Integer:
    1. IF value > 0:
        2. ENSURE value > 1
            OTHERWISE THROW "outside range"
    3. ACHIEVE "done" @trace("REQ-3") AS TRACE_FIRST @trace("REQ-3") AS TRACE_SECOND
        POSTCONDITION: "Value checked"
ENSURE: "Always checked"
MODEL "review":
    TYPE: Alloy
    FILE: "review.als"
ASSUMPTION "Storage remains available":
    AFFECTS: [Checker]
    CONSEQUENCE: "Calls can complete"
"""
    (tmp_path / "review.als").write_text("module review\n")
    return write_spec(tmp_path, VERIFIED, "sample", body, "1.2")


def test_cpc_inventory_maps_occurrences_to_semantic_nodes(tmp_path, checked_spec):
    """AST-AT-003, AST-AC-002-01, AST-AC-002-02, AST-AC-002-03, and AST-AC-003-01."""
    artifact, _ = export(tmp_path)
    assert artifact["kind"] == "SemanticSystem"
    assert artifact["semantic_validate"]["status"] == "PASSED"
    assert artifact["semantic_validate"]["gasd_file_version"] == artifact["metadata"]["version"] == "1.2"
    assert {"parser_version", "build_time", "validation_time"} <= artifact["semantic_validate"].keys()
    assert artifact["source_inventory_version"] in (1, "1")
    inventory = artifact["source_inventory"]
    assert len({row["identity"] for row in inventory}) == len(inventory)
    assert all(row["path"] == VERIFIED and row["line"] >= 1 and row["column"] >= 0 for row in inventory)
    mapped = [(row, resolve(artifact, row["pointer"])) for row in inventory]
    annotations = {node["alias"]: row for row, node in mapped if row["kind"] == "annotation"}
    text = checked_spec.read_text().splitlines()
    line_number, line = next((i, line) for i, line in enumerate(text, 1) if "TRACE_FIRST" in line)
    for alias, start in zip(("TRACE_FIRST", "TRACE_SECOND"), (line.index("@trace"), line.rindex("@trace"))):
        row = annotations[alias]
        assert (row["line"], row["column"]) == (line_number, start)
        assert "sample" in row["owner"] and "validate" in row["owner"]
    assert any(node.get("name") == "Checker" for _, node in mapped if isinstance(node, dict))
    assert any(node.get("operation") == "THROW" for _, node in mapped if isinstance(node, dict))
    assert any(node.get("operator") == "IS" for _, node in mapped if isinstance(node, dict))
    assert {"MIN_ID", "TRACE_FIRST", "TRACE_SECOND"} <= annotations.keys()
    assert "review.als" in json.dumps(artifact["models"])
    assert "Always checked" in json.dumps(artifact)


@pytest.mark.parametrize("mutation", ["drop", "duplicate", "move", "argument", "scope", "type", "literal"])
def test_cpc_detects_final_export_mutation(tmp_path, checked_spec, mutation, monkeypatch, capsysbinary):
    """AST-AT-003 and AST-AC-002-02. Alter the final semantic AST with syntax fixed."""
    from Impl import cli
    from Impl.semantic.SemanticASTExporter import SemanticASTExporter

    serialize = SemanticASTExporter.to_json

    def altered(self, *args, **kwargs):
        document = json.loads(serialize(self, *args, **kwargs))
        namespace = document["namespaces"]["sample"]
        flow = namespace["flows"]["validate"]
        step = next(item for item in flow["pipeline"] if item["stepNumber"] == 3)
        annotations = step["annotations"]
        if mutation == "drop":
            annotations.pop()
        elif mutation == "duplicate":
            annotations.append(annotations[0])
        elif mutation == "move":
            flow["annotations"].append(annotations.pop())
        elif mutation == "scope":
            annotations[0]["scope"] = "GLOBAL"
        elif mutation == "argument":
            annotations[0]["arguments"]["value"] = "REQ-4"
        elif mutation == "type":
            namespace["types"]["RecordId"]["fields"]["id"]["typeRef"]["baseType"] = "String"
        else:
            step["targetExpression"]["value"] = '"different"'
        return json.dumps(document, indent=2)

    monkeypatch.setattr(SemanticASTExporter, "to_json", altered)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["gasd_parser", "--json", VERIFIED])
    with pytest.raises(SystemExit) as stopped:
        cli.main()
    out, err = capsysbinary.readouterr()
    assert stopped.value.code != 0 and not out, err.decode()
    report = json.loads(err)
    assert report["success"] is False and "semantic_ast_sha512" not in report
    diagnostics = [error for item in report["reports"] for error in item["errors"]]
    assert any(
        "reconcil" in json.dumps(error).lower() and error.get("location", {}).get("line", 0) >= 5
        for error in diagnostics
    )


@pytest.mark.parametrize("destination", [None, "ast.json"])
def test_cpc_publishes_exact_external_digest(tmp_path, checked_spec, destination):
    """AST-AC-003-01 and AST-AC-003-02. The report identifies the delivered bytes."""
    artifact, payload = export(tmp_path, destination=destination)
    embedded = artifact["semantic_validate"]["semantic_ast_bytes_sha512"].encode()
    assert sha512(payload.replace(embedded, b"0" * 128, 1)).hexdigest().encode() == embedded
    assert "semantic_ast_sha512" not in artifact


def test_cpc_failure_never_replaces_previous_ast(tmp_path, checked_spec):
    """AST-AC-003-01 and AST-AC-003-02."""
    original = checked_spec.read_bytes()
    _, saved = export(tmp_path, destination="ast.json")
    write_spec(tmp_path, VERIFIED, "sample", "TYPE Item: value: BadType", "1.2")
    process = run_cli(tmp_path, "--json", "--ast-output", "ast.json", VERIFIED)
    assert process.returncode != 0 and not process.stdout
    report = json.loads(process.stderr)
    assert "semantic_ast_sha512" not in report and report["success"] is False
    assert report.get("semantic_validate", {}).get("status") != "PASSED"
    assert (tmp_path / "ast.json").read_bytes() == saved
    checked_spec.write_bytes(original)
    blocked = tmp_path / "blocked"
    blocked.mkdir()
    process = run_cli(tmp_path, "--json", "--ast-output", blocked, VERIFIED)
    assert process.returncode != 0 and not process.stdout
    assert "semantic_ast_sha512" not in json.loads(process.stderr)


def test_syntax_only_output_has_no_verified_inventory(tmp_path, checked_spec):
    """AST-AC-003-01. Syntax-only output does not qualify as a validated AST."""
    process = run_cli(tmp_path, "--json", "--no-validate", VERIFIED)
    assert process.returncode == 0, process.stderr.decode()
    assert "source_inventory" not in json.loads(process.stdout)
    assert "semantic_ast_sha512" not in json.loads(process.stderr)


def test_default_file_export_is_source_checked(tmp_path, checked_spec):
    """AST-AC-003-01 and AST-AC-003-02 without the JSON-report option."""
    process = run_cli(tmp_path, "--ast-output", "ast.json", VERIFIED)
    assert process.returncode == 0, process.stderr.decode()
    payload = (tmp_path / "ast.json").read_bytes()
    artifact = json.loads(payload)
    assert not process.stdout
    assert artifact["semantic_validate"]["status"] == "PASSED"
    assert artifact["source_inventory_version"] == 1 and artifact["source_inventory"]
    assert f"semantic_ast_sha512: {sha512(payload).hexdigest()}" in process.stderr.decode()


def test_default_export_preserves_legacy_decision_and_flow_annotations(tmp_path):
    example = ROOT / "Specs/examples/gasd-1.1/operational_concerns.gasd"
    source = tmp_path / example.name
    source.write_bytes(b"VERSION 1.1\n" + example.read_bytes())
    artifact, _ = export(tmp_path, source)
    namespace = artifact["namespaces"]["example.operational_concerns"]
    decision = namespace["decisions"]["Infrastructure Provider"]
    flow = namespace["flows"]["process_order"]
    assert decision["annotations"][0]["name"] == "status"
    assert flow["annotations"][0]["name"] == "authorized"
    for annotation in (decision["annotations"][0], flow["annotations"][0]):
        location = annotation["sourceMap"]
        occurrence = next(item for item in artifact["source_inventory"]
                          if item["kind"] == "annotation" and item["line"] == location["startLine"]
                          and item["column"] == location["startCol"])
        assert resolve(artifact, occurrence["pointer"]) == annotation


def test_default_export_verifies_legacy_inline_otherwise(tmp_path):
    source = write_spec(tmp_path, VERIFIED, "search", (
        "FLOW search(items):\n"
        '    1. ENSURE items IS_SORTED OTHERWISE THROW IllegalStateException("Sort items")'
    ))
    artifact, _ = export(tmp_path, source)
    step = artifact["namespaces"]["search"]["flows"]["search"]["pipeline"][0]
    assert step["targetExpression"]["value"] == "items IS_SORTED"
    branch = step["otherwisePath"]
    assert branch["operation"] == "THROW"
    assert branch["targetExpression"]["value"] == 'IllegalStateException("Sort items")'
    occurrence = next(item for item in artifact["source_inventory"] if item["kind"] == "branch")
    assert resolve(artifact, occurrence["pointer"]) == branch
