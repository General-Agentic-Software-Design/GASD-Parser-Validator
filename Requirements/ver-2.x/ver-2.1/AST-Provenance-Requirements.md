# AST Provenance Requirements

`gasd_parser` reads the authored `.gasd` specification and exports the validated semantic AST as JSON, for example `ast.json`. The exported JSON embeds the logical path and SHA-512 digest of each GASD source used in the parse. POX and Scaffgen consume this artifact directly. [POT provenance requirements](../pox/POT-AST-Provenance-Requirements.md) · [Scaffgen AST input requirements](../scaffgen/Scaffgen-AST-Input-Requirements.md)

## Source inventory in the semantic AST

Every successfully exported semantic AST must contain a nonempty `provenance.sources` array. Include each GASD entry file and every resolved imported GASD file consumed by that AST. Each inventory entry contains these fields.

| Field | Requirement |
|---|---|
| `path` | Stable logical source path consistent with the AST source locations. Emit one entry per path and sort entries by path for deterministic output. |
| `sha512` | SHA-512 of the exact GASD source bytes supplied to parsing, encoded as 128 lowercase hexadecimal characters. |

Calculate each digest from the captured input bytes before decoding or normalizing line endings. Parse from that same capture so an edit on disk during export cannot pair the AST with a digest from a later revision. Include a source only when it contributed to that AST. If a required source cannot be read or identified, report the failure and withhold a successful semantic AST export.

## AST fingerprints in the parse report

When the parser or ingestion flow emits `parse-report.json` for a successful semantic AST export, the report must contain a `semantic_validate` object with both fingerprint fields, regardless of the GASD input version. Encode each SHA-512 digest as 128 lowercase hexadecimal characters. If the report has no successfully exported semantic AST, omit both fingerprint fields.

| Report field | Bytes hashed |
|---|---|
| `semantic_validate.semantic_ast_bytes_sha512` | Every byte in the final `ast.json`, including the source inventory, any validation metadata, and any trailing newline. |
| `semantic_validate.semantic_ast_content_sha512` | The canonical UTF-8 JSON representation of the validated semantic model. |

Define and version the rules for projecting and serializing the semantic model so consumers can reproduce `semantic_ast_content_sha512`. Exclude source provenance, diagnostic source locations, export and validation timestamps, generated node IDs, and derived hashes. Preserve authored semantic values, resolved symbol identities and references, and ordering where it affects meaning. Use stable semantic identities for any references to nodes with generated IDs, and normalize unordered collections deterministically.

Obelisk supplies the same exported artifact bytes to POX and Scaffgen. Independent exports can produce different artifact fingerprints when timestamps, generated IDs, or serialization change. Exports with the same canonical semantic model produce the same semantic fingerprint.

### Semantic content fingerprint, version 1

`parse-report.json` identifies these rules with `semantic_validate.semantic_ast_content_version` set to `"1"`. Use the semantic AST JSON from the same successful export as the input to this projection.

1. Omit the root `provenance`, `semantic_validate`, and `compilationUnit` fields, and omit `metadata.files`. Project imports from `compilationUnit.fileNodes` into a root `imports` array when there are import edges. Each edge has `namespace` from its source file node, `alias` from the import or `null`, and `target`. The target is `{"namespace": name}` when the import path identifies a file node and `{"external": path}` otherwise. Sort edges by canonical JSON and collapse identical edges.
2. Omit generated `id` and diagnostic `sourceMap` on semantic nodes, the derived `hash` on `ResolvedContract`, and `sourceFile`, `line`, `column`, `endLine`, and `endColumn` on embedded syntactic AST nodes. Preserve other fields, including authored documentation and authored timestamps. Annotation argument dictionaries retain their full JSON data, including keys that match internal AST field names.
3. Replace a `symbolId` that refers to a generated ID with `{"node": [path segments]}`. Paths start at the projected root. Object segments use their key and ordered array segments use their zero-based index. Unordered declaration members use their `kind` and `name`, or their `kind` and `text` for unnamed constraints. For ambiguous or unnamed members, append their canonical projected shape with generated link targets represented as `null`. A node reachable by several paths uses the first path in canonical JSON order. Ordinary resolved symbol names remain strings.
4. Sort these arrays by canonical JSON and retain multiplicity. At the root, sort `globalConstraints`, `contracts`, `models`, and `assumptions`. In `metadata`, sort `target` and `trace`. Sort `SemanticFlowStep.dependsOn`, resolved expression `dependencies`, `ResolvedComponent.dependencies`, `ResolvedComponent.resources`, `ResolvedComponent.provides`, `ResolvedComponent.requires`, `ResolvedDecision.affectedComponents`, `ResolvedAssumption.affected`, and `ResolvedResource.permissions`. Preserve order for other arrays, including cases, guards, flow steps, parameters, generic arguments, and annotations.
5. Sort object keys by Unicode code point. Serialize compact JSON with ASCII escapes for non-ASCII characters, no surrounding whitespace or trailing newline, exact integers, and the Python shortest round-trip JSON representation of finite floats. Reject non-finite values. The reference encoder is `json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)` followed by UTF-8 encoding. Apply SHA-512 to those bytes.

## Acceptance criteria

| Case | Expected result |
|---|---|
| Entry file with an imported GASD dependency | The AST inventories both logical paths and their independently calculated SHA-512 digests. |
| Edit to the entry file or a resolved import | A new export records the changed source digest under the same logical path. |
| A source changes on disk after the parser captures it | The exported semantics and SHA-512 refer to the captured revision. |
| Unreadable required source | The parser reports the affected path and exits unsuccessfully. |
| Successful semantic AST export with a parse report | `semantic_validate` contains both lowercase SHA-512 digests. Hashing the exact AST file reproduces `semantic_ast_bytes_sha512`, and hashing the canonical semantic model reproduces `semantic_ast_content_sha512`. |
| Repeat export with different validation timestamps or generated node IDs | `semantic_ast_bytes_sha512` changes and `semantic_ast_content_sha512` stays the same. |
| Comment-only edit that leaves the semantic model unchanged | The edited source digest and `semantic_ast_bytes_sha512` change. `semantic_ast_content_sha512` stays the same. |
| Edit that changes the validated semantic model, such as changing a resolved field type | Both fingerprints change. |
| Parse report without a successful semantic AST export | Both fingerprint fields are absent. |

## User stories

**Epic:** `EPIC-PARSER-001`

### US-AST-PROVENANCE-014 · Identify the source revisions used by the AST

As a GASD tooling integrator, I want the semantic AST to identify every GASD source revision it used, so that I can trace an exported model to the exact inputs that produced it.

| ID | Scenario | Observable result | Source |
|---|---|---|---|
| `AC-AST-PROVENANCE-014-01` | Export a validated AST from one or more GASD inputs. | `ast.json` contains a nonempty `provenance.sources` array of objects with `path` and `sha512` fields. The paths match exactly the contributing entry and resolved import paths, including transitive imports. Each path occurs once, follows the AST source-location convention, and retains its logical identity across exports in the same path context. Entries are sorted by `path`. When standard input contributes, its `path` is `stdin`. | [Source inventory](#source-inventory-in-the-semantic-ast) · [Existing source identifiers](relative_source_map_paths.md#acceptance-criteria) |
| `AC-AST-PROVENANCE-014-02` | Capture source bytes and parse them, including a case where a source file is edited on disk after capture. | Each `provenance.sources[].sha512` matches `^[0-9a-f]{128}$` and equals SHA-512 over its captured bytes before decoding or line-ending normalization. The AST reflects the captured revision, even when the file on disk changes before parsing or serialization finishes. | [Source inventory](#source-inventory-in-the-semantic-ast) |
| `AC-AST-PROVENANCE-014-03` | Make a byte-changing edit to a contributing entry file or resolved import at the same path and export again successfully. | The affected inventory entry retains its `path` and its `sha512` matches the new capture. Entries for unchanged sources retain their digests. | [Acceptance criteria](#acceptance-criteria) |
| `AC-AST-PROVENANCE-014-04` | Attempt an export when a required entry file or GASD import cannot be read or assigned a logical path. | The parser diagnostic identifies the affected source path, the CLI exits with a nonzero status, and the run produces no successful semantic AST export. | [Source inventory](#source-inventory-in-the-semantic-ast) |

#### Subtasks

- Capture each input's bytes with its logical path in the parser's source-loading path. Give parsing and digest calculation the same capture.
- Have the semantic AST exporter write the sorted, deduplicated `provenance.sources` inventory. Surface read and source-identity failures through parser diagnostics and the CLI exit status.

### US-AST-PROVENANCE-015 · Verify the exact exported AST artifact

As an Obelisk integration developer, I want the parse report to identify the exact semantic AST artifact, so that I can verify POX and Scaffgen received the same bytes, including source provenance.

| ID | Scenario | Observable result | Source |
|---|---|---|---|
| `AC-AST-PROVENANCE-015-01` | A validated semantic AST is successfully exported and a parse report is emitted. | SHA-512 recomputed over the complete bytes delivered to the selected AST destination equals `parse-report.json`'s `semantic_validate.semantic_ast_bytes_sha512`. The bytes include the source inventory, validation metadata when present, and a trailing newline when present. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |
| `AC-AST-PROVENANCE-015-02` | The parser or ingestion flow emits `parse-report.json` for a successful semantic export of any supported GASD input version. | The report has a `semantic_validate` object containing both `semantic_ast_bytes_sha512` and `semantic_ast_content_sha512`. Both values are strings matching `^[0-9a-f]{128}$`. This applies whether the AST itself carries a validation marker. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |
| `AC-AST-PROVENANCE-015-03` | The parser or ingestion flow emits a report without a successful semantic AST export, as in a validation failure, a syntax-only export, or a failed AST write. | Both fingerprint keys are absent from the current report, even if an earlier AST file exists at the destination. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |
| `AC-AST-PROVENANCE-015-04` | Obelisk supplies an exported semantic AST to POX and Scaffgen. | The bytes delivered to each consumer equal the original export byte-for-byte, and each SHA-512 digest equals the reported `semantic_ast_bytes_sha512`. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |

#### Subtasks

- Have AST export provide the final byte sequence and the outcome of writing it to the selected destination. Compute the artifact fingerprint over that sequence.
- Have the parser or ingestion report producer write both fields under `semantic_validate` for a successful semantic AST export. Use the final export outcome to decide whether the report includes them.
- Verify that the Obelisk handoff delivers the original export bytes to both consumers.

### US-AST-PROVENANCE-017 · Identify equivalent semantic AST content

As a semantic AST consumer, I want a reproducible fingerprint of the validated model, so that I can detect semantic changes across independent exports.

| ID | Scenario | Observable result | Source |
|---|---|---|---|
| `AC-AST-PROVENANCE-017-01` | A consumer independently encodes the validated model with the documented projection and serialization version applicable to the export. | SHA-512 over the canonical UTF-8 JSON equals `semantic_validate.semantic_ast_content_sha512`. The versioned rules define the included fields, reference identities, collection ordering, and JSON encoding closely enough to reproduce the same bytes. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |
| `AC-AST-PROVENANCE-017-02` | Produce canonical JSON for a model with resolved references, authored semantic values, and ordered and unordered collections. | The output retains the authored values and the meaning of resolved identities, references, and order. References to generated nodes use stable semantic identities. Unordered collections have deterministic order. Source provenance, diagnostic locations, export and validation timestamps, generated node IDs, and derived hashes are excluded. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) |
| `AC-AST-PROVENANCE-017-03` | Using the same rules version, compare successful exports with different validation timestamps, remapped generated node IDs, or an ordinary comment edit that leaves the semantic model equivalent. | The content fingerprints match and the byte fingerprints differ in each comparison. In the comment case, the edited source digest also differs at the same logical path. | [Acceptance criteria](#acceptance-criteria) |
| `AC-AST-PROVENANCE-017-04` | Using the same rules version, compare successful exports after a valid edit changes an authored semantic value, a resolved reference target, or order that affects meaning. | Both fingerprints differ. Changing a reference target is observable even when both targets remain present in the model. | [AST fingerprints](#ast-fingerprints-in-the-parse-report) · [Acceptance criteria](#acceptance-criteria) |

#### Subtasks

- Publish versioned projection and serialization rules that identify the version applicable to an export. Specify included and excluded fields, stable reference identities, collection and object-key ordering, and the encoding of JSON values.
- Have the parser project the validated model and compute SHA-512 from its canonical UTF-8 JSON. Supply the result to the report producer as `semantic_ast_content_sha512`.

## Story acceptance and regression tests

| Test ID | Covers | Scenario and expected result |
|---|---|---|
| `AT-AST-PROVENANCE-014-01` | `AC-AST-PROVENANCE-014-01`, `AC-AST-PROVENANCE-014-02` | Export an entry file that resolves an import. Verify that both logical paths appear once, sorted and consistent with the AST source locations. Keep an unrelated GASD file beside them and verify its absence. Use CRLF in one contributing file and independently hash each raw source to check the reported digests. |
| `AT-AST-PROVENANCE-014-02` | `AC-AST-PROVENANCE-014-03` | Edit the entry file and then a resolved import in separate runs. Verify that each new export updates the digest at the edited file's logical path while preserving the digest at the unchanged path. |
| `AT-AST-PROVENANCE-014-03` | `AC-AST-PROVENANCE-014-04` | For both an entry file and a resolved import, exercise a read failure and a failure to establish the logical path. Verify the affected path in the diagnostic, unsuccessful exit, and absence of a successful semantic AST export in each case. |
| `AT-AST-PROVENANCE-014-04` | `AC-AST-PROVENANCE-014-01` | Export a standalone entry file and verify that the inventory contains its path. Then export two entry files with a shared dependency that has a resolved transitive import. Verify that the two entry paths, the shared dependency path, and the transitive import path appear exactly once in sorted order. |
| `RT-AST-PROVENANCE-014-01` | `AC-AST-PROVENANCE-014-02` | After byte capture and before parsing, replace the source on disk with a valid revision that changes a semantic value. Repeat for an entry file and a resolved import. Verify that both the exported value and the source digest correspond to the captured revision. |
| `RT-AST-PROVENANCE-014-02` | `AC-AST-PROVENANCE-014-01`, `AC-AST-PROVENANCE-014-02` | Pipe the raw bytes of a valid GASD fixture into `gasd_parser --json -`. Verify that the exported `provenance.sources` contains one entry with `path` equal to `stdin` and `sha512` equal to the independently computed SHA-512 of the piped bytes. |
| `AT-AST-PROVENANCE-015-01` | `AC-AST-PROVENANCE-015-01`, `AC-AST-PROVENANCE-015-02` | For each supported GASD input version, run `gasd_parser --json --ast-output ast.json input.gasd` and capture the JSON report from stderr. Repeat with `--json` alone and capture the AST from stdout. In each run, independently hash the raw bytes from the selected destination, compare to `semantic_ast_bytes_sha512`, and verify both report fields and their format. Apply the same checks to any ingestion-produced report. |
| `AT-AST-PROVENANCE-015-02` | `AC-AST-PROVENANCE-015-03` | Check reports from a validation failure, a syntax-only AST export, and a failed write after semantic validation succeeds. Exercise a failed run with an earlier AST artifact at the destination. Verify that both fingerprint keys are absent in each report. |
| `AT-AST-PROVENANCE-015-03` | `AC-AST-PROVENANCE-015-04` | Compare the copies delivered to POX and Scaffgen to the original export and verify their hashes against the same report value. |
| `RT-AST-PROVENANCE-015-01` | `AC-AST-PROVENANCE-015-01` | Generate reports from two serialized semantic AST fixtures that differ only by a trailing LF. Verify that the exact-byte hashes differ and that each equals SHA-512 over all bytes of its fixture. |
| `AT-AST-PROVENANCE-017-01` | `AC-AST-PROVENANCE-017-01`, `AC-AST-PROVENANCE-017-02` | Use the documented, versioned rules to independently construct the canonical UTF-8 JSON for a fixture with source provenance, diagnostic locations, export and validation timestamps, derived hashes, authored values, and references to generated nodes. Include ordered and unordered collections. Verify that the report matches the SHA-512 of the expected canonical bytes. |
| `AT-AST-PROVENANCE-017-02` | `AC-AST-PROVENANCE-017-04` | Change the type of a resolved field and export the valid model again. Verify that both fingerprints change. |
| `RT-AST-PROVENANCE-017-01` | `AC-AST-PROVENANCE-017-02`, `AC-AST-PROVENANCE-017-03` | Compare exports of the same sources with a different validation timestamp. Separately compare exports with remapped generated node IDs and references that still point to the same nodes. Verify that the byte fingerprint changes and the content fingerprint stays the same in each comparison. |
| `RT-AST-PROVENANCE-017-02` | `AC-AST-PROVENANCE-017-03` | Edit an ordinary GASD comment without changing the model. Verify that the edited source digest and byte fingerprint change and the content fingerprint is identical. |
| `RT-AST-PROVENANCE-017-03` | `AC-AST-PROVENANCE-017-02`, `AC-AST-PROVENANCE-017-04` | Permute an unordered collection and verify that the content fingerprint stays the same. Reorder a sequence whose order affects meaning while keeping both models valid, and verify that both fingerprints change. |
| `RT-AST-PROVENANCE-017-04` | `AC-AST-PROVENANCE-017-02`, `AC-AST-PROVENANCE-017-04` | Export valid models with two distinct resolved symbols present in both. Change a reference from the first symbol to the second. Independently derive the canonical bytes for each target and check the reported content digests against them. Verify that both fingerprint values differ between exports. |
