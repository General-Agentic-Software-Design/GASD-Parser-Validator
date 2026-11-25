# GASD Parser Semantic AST Requirements

**Status** Implemented in GASD Parser 2.1.11 for the Ver-1.1 CPC parser handoff

`gasd_parser` MUST produce one source-checked semantic AST for each CPC input. The export MUST preserve the GASD constructs that drive scaffold generation and proof obligations, and identify the exact source bytes it represents. POX and Scaffgen consume this export through their respective input contracts. [CPC parser provenance](../../../../SEED-CPC-Spec/CPC-System/parser/GASD-Parser-AST-Provenance-Requirements.md) · [POX AST input](../../../../Proof-Obligation-Extractor/Requirements/Ver-1.1/POX_AST_Input_Requirements.md) · [Scaffgen AST input](../../../../SEED-CPC-Spec/CPC-System/scaffgen/Scaffgen-AST-Input-Requirements.md)

## AST-REQ-001 Capture and identify every GASD source

- **AST-AC-001-01.** The parser MUST capture the bytes of each entry source and every resolved import it consumes. It MUST parse from that capture and compute SHA-512 over the same bytes before text decoding or line-ending normalization.
- **AST-AC-001-02.** The AST MUST contain a nonempty `provenance.sources` array. Each entry MUST contain the logical `path` used by AST source locations and the source's `sha512` as 128 lowercase hexadecimal characters. Emit one entry per logical path, sorted by path. Include transitive imports and retain their source ownership.
- **AST-AC-001-03.** The parser MUST report unreadable sources, unresolved imports, and conflicting logical paths as source-located errors. A successful export requires a complete inventory of its captured inputs.

## AST-REQ-002 Verify that GASD constraints survive parsing

- **AST-AC-002-01.** The parser MUST build the expected inventory of source occurrences from its syntax representation before constructing the semantic AST. The inventory MUST identify each occurrence by its construct, logical source path and coordinates, and qualified owner. Include flow, numbered step, branch, and annotation `AS` identity where applicable. Distinct occurrences on the same line MUST remain independently traceable.
- **AST-AC-002-02.** Before export, the parser MUST reconcile that inventory with the semantic AST and preserve the meaning of each occurrence. It MUST detect missing, duplicated, moved, or changed semantics, including wrong owners, arguments, types, literals, or scope. A structured diagnostic MUST identify the affected source occurrence when reconciliation fails.
- **AST-AC-002-03.** The successful AST MUST include the verified `source_inventory`. The export schema MUST define its supported revision, occurrence identity, source-location conventions, and how the inventory maps to the semantic AST. An inventory entry MUST resolve to the corresponding semantic construct, including declarations used by Scaffgen and constraints used by POX. [Source and obligation coverage](../../../../Proof-Obligation-Extractor/Requirements/Ver-1.0/Extraction_patch_requirements.md#px-req-007--make-coverage-a-semantic-completeness-gate)

| GASD content | Semantic information the export must preserve |
| --- | --- |
| Declarations and types | Qualified components, interfaces, operations, parameters, result and error types, and data fields with their constraints. |
| Flows and branches | Numbered steps, operation kind, operands and literals, guards, dependencies, branch identity and order, return values, and exceptional or failure actions. |
| Annotations and traces | Names, arguments, source locations, attachment and scope, `AS` occurrence identifiers, and upstream trace references. |
| Conditions and contracts | Preconditions and postconditions, observation or result fields, operators and expected values, ordered contract cases and guards, specified outcomes, and explicit entry-point-to-flow mappings. |
| Assumptions, invariants, and models | Their declared conditions, scope, affected constructs, consequences, and relevant model or import references. |

## AST-REQ-003 Publish one validated AST artifact

- **AST-AC-003-01.** An AST eligible for CPC MUST carry the complete `semantic_validate` object with `status: "PASSED"`, the parser and GASD versions, `provenance.sources`, and the verified `source_inventory`. The parser MUST complete semantic validation and source reconciliation before it publishes a successful export.
- **AST-AC-003-02.** The parser or CPC ingestion step MUST compute `semantic_ast_sha512` over the final exported AST JSON bytes, including whitespace and any trailing newline. Record that value in the parse report or run manifest outside the AST artifact. This digest identifies the exact export. The digests in `provenance.sources` identify the captured GASD files.

## Acceptance tests

| Test | Action | Required result |
| --- | --- | --- |
| **AST-AT-001** | Export a GASD entry file with a direct import and a transitive import. Independently hash the captured files. | Every consumed file appears once with its exact SHA-512 value. Source locations resolve to those logical paths. |
| **AST-AT-002** | Change or replace a source after its bytes are captured. Also attempt an export with an unreadable required import. | Semantics and hashes in the successful capture refer to the same bytes. An unreadable required source produces an error and no successful export. |
| **AST-AT-003** | Parse a fixture with multiple annotations on one line, typed postconditions, and nested failure branches. Independently compare against the source syntax. Repeat with a test export path that drops or changes one semantic occurrence. | The valid case retains all occurrences and ownership. The changed case identifies the missing or changed source occurrence and fails source reconciliation. |

## Implementation in 2.1.11

Semantic validation and source reconciliation run by default when exporting a semantic AST to a file or stdout. `gasd_parser --json --ast-output ast.json input.gasd` writes the AST to `ast.json` and the JSON parse report to stderr. Omitting `--ast-output` streams the AST to stdout. Omitting `--json` for a file export selects a human-readable report with the same `semantic_ast_sha512` digest. A syntax-only export with `--no-validate` is ineligible for this handoff. [CLI usage and inventory schema](../../../README.md#cpc-ast-export) · [Executable acceptance tests](../../../Impl/tests/acceptance/test_cpc_semantic_ast.py)

## Implementation audit

**Partially implemented in GASD Parser 2.1.10** (`1f6a765` on branch `2.1`). The parser captured and hashed source files and computed a SHA-512 digest of the exported AST. The CPC handoff lacked occurrence-level verification. The findings below describe that audited baseline.

| Criterion | Status | Finding |
| --- | --- | --- |
| `AST-AC-001-01` | Implemented | The parser computes SHA-512 over the captured bytes before decoding or line-ending normalization and parses from that same capture. [Source capture](../../../Impl/parser/ParseTreeAPI.py#L12) |
| `AST-AC-001-02` | Implemented | The entry file, direct import, and transitive import each appeared once in sorted `provenance.sources`. Their SHA-512 digests matched independent hashes of the original bytes, and the semantic declarations retained the matching logical source paths. [Source provenance export](../../../Impl/semantic/SemanticASTExporter.py#L16) · [Import provenance tests](../../../Impl/tests/acceptance/test_ast_provenance.py#L62) |
| `AST-AC-001-03` | Partial | Unreadable sources, missing `.gasd` imports, and conflicting logical paths blocked export. The I/O diagnostics identified the affected path. An unresolved import of `./missing/types.txt` still allowed a successful export. [Import discovery and source errors](../../../Impl/cli.py#L118) · [Import resolver](../../../Impl/semantic/ImportResolver.py#L28) |
| `AST-AC-002-01` | Missing | The parser has no independent syntax-derived occurrence inventory before semantic AST construction. [Syntax and semantic AST construction](../../../Impl/cli.py#L135) |
| `AST-AC-002-02` | Missing | The parser has no pre-export reconciliation gate or structured diagnostic for a lost occurrence. Additional fixtures exposed omissions in the exported semantic AST, including a field constraint, a top-level `ENSURE`, and a model's `FILE` reference. [Semantic conversion](../../../Impl/semantic/SemanticPipeline.py#L397) · [Semantic AST serialization](../../../Impl/semantic/SemanticNodes.py#L584) |
| `AST-AC-002-03` | Missing | The exported AST has no `source_inventory` or versioned schema that maps verified source occurrences to semantic constructs. [Semantic AST export](../../../Impl/semantic/SemanticASTExporter.py#L38) |
| `AST-AC-003-01` | Partial | Successful GASD 1.2 exports carry `semantic_validate.status` set to `PASSED`, the parser and GASD versions, and `provenance.sources`. The marker currently certifies semantic validation alone. The export still needs source reconciliation and the verified occurrence inventory. [Validation marker and export](../../../Impl/cli.py#L248) |
| `AST-AC-003-02` | Partial | The report's `semantic_validate.semantic_ast_bytes_sha512` matches the exact exported JSON bytes, including a trailing newline when present. The required `semantic_ast_sha512` field was absent from the parser report and the Obelisk ingestion code reviewed. [Parser fingerprint](../../../Impl/semantic/ASTProvenance.py#L165) · [Trailing newline test](../../../Impl/tests/acceptance/test_ast_provenance.py#L241) · [Obelisk ingestion](../../../../Obelisk/Impl/internal/adapters/adapters.go#L286) |

### Acceptance test results

The audit ran **109 targeted repository tests**, all passing, and used additional parser export fixtures to verify the criteria above.

| Test | Result | Observed behavior |
| --- | --- | --- |
| `AST-AT-001` | Passed | The entry file, direct import, and transitive import appeared once with independently verified SHA-512 digests. Their semantic declaration locations resolved to the corresponding logical paths. |
| `AST-AT-002` | Passed | Editing either the entry file or a resolved import after capture left the parsed semantics and digest tied to the captured bytes. An unreadable required import produced an error and blocked the export. [Capture test](../../../Impl/tests/acceptance/test_ast_provenance.py#L102) · [Unreadable source test](../../../Impl/tests/acceptance/test_ast_provenance.py#L173) |
| `AST-AT-003` | Failed | The baseline kept the typed contract postcondition and nested `OTHERWISE THROW` but dropped two same-line annotations from a numbered flow step. In a separate run, removing a component annotation from the validated semantic tree before export still produced an AST marked `PASSED`. The report indicated success, the CLI exited `0`, and no reconciliation diagnostic identified the omission. |

## User stories

### AST-US-001 Identify the GASD sources used by an export

As a CPC run operator, I want the semantic AST to identify the exact GASD bytes used for each source so I can reproduce the input and trace imported declarations to their defining files.

**Source** [AST-REQ-001](#ast-req-001-capture-and-identify-every-gasd-source) · [Existing provenance story](AST-Provenance-Requirements.md#us-ast-provenance-014--identify-the-source-revisions-used-by-the-ast)

**Implementation status** In 2.1.11, validated exports capture every required source and reject unresolved imports regardless of suffix. [Implementation](#implementation-in-2111) · [2.1.10 audit](#implementation-audit)

Run from a fixture root where `entry.gasd` imports `imports/direct.gasd`, which imports `imports/nested/leaf.gasd`. Give each source a distinct declaration and write one import with CRLF line endings. Keep `unrelated.gasd` beside the entry file.

| Criterion | Fixture and action | Pass condition |
| --- | --- | --- |
| `AST-AC-001-01` | Independently hash the original file bytes. In separate runs, replace a declaration on disk in the entry, direct import, or transitive import after that file is captured and before it is parsed. | The exported declaration reflects the original value and its source digest matches SHA-512 of the captured bytes, including the original line endings. |
| `AST-AC-001-02` | From the fixture root, export the complete import chain with the unrelated file present. Repeat with relative and absolute CLI arguments for `entry.gasd`. | Both runs emit exactly `entry.gasd`, `imports/direct.gasd`, and `imports/nested/leaf.gasd` in `provenance.sources`, in that order with one record per path. Each `sha512` is 128 lowercase hexadecimal characters and equals the independent digest for that file. Each representative declaration's `sourceMap.file` equals the `path` of its own defining file's inventory record. [Relative path contract](relative_source_map_paths.md#acceptance-criteria) |
| `AST-AC-001-03` | Start each run with a fresh output destination. Inject a read failure for the entry and for a required import in separate runs. Exercise unresolved direct and transitive imports, including paths with and without a `.gasd` suffix. Force two different captures to resolve to the same logical path. | Each run reports an error that identifies the affected path and, where applicable, the import site. The CLI exits nonzero and publishes no successful AST. |

**Subtasks**

| Owner | Scope and deliverable | Criteria |
| --- | --- | --- |
| Parser maintainer | Maintain the single-capture input path and produce a complete, sorted `provenance.sources` array whose paths match the semantic AST locations. Raise source diagnostics before export when capture, resolution, or logical path identity fails. | `AST-AC-001-01` through `AST-AC-001-03` |
| Parser test maintainer | Retain the capture and provenance regressions. Deliver import-chain and capture-replacement fixtures for `AST-AT-001` and `AST-AT-002`, plus negative fixtures for unresolved imports and conflicting logical paths. [Source provenance tests](../../../Impl/tests/acceptance/test_ast_provenance.py) | `AST-AC-001-01` through `AST-AC-001-03` |

### AST-US-002 Verify source occurrences against the semantic AST

As a POX or Scaffgen integrator, I want each source occurrence to resolve to its corresponding semantic construct so generated proof obligations and scaffolds preserve the authored design.

**Source** [AST-REQ-002 and its construct coverage table](#ast-req-002-verify-that-gasd-constraints-survive-parsing) · [POX AST input contract](../../../../Proof-Obligation-Extractor/Requirements/Ver-1.1/POX_AST_Input_Requirements.md)

**Implementation status** In 2.1.11, the parser reconciles syntax-derived occurrences before export and emits the verified revision 1 inventory. [Implementation](#implementation-in-2111) · [2.1.10 audit](#implementation-audit)

Use authored fixture expectations or an independent syntax walk as the test oracle. Put two annotations with the same name and arguments and different `AS` identifiers on one numbered step. Include a typed postcondition, a nested failure branch, and an imported declaration. Add fixtures as needed to exercise every construct group below.

| Criterion | Fixture and action | Pass condition |
| --- | --- | --- |
| `AST-AC-002-01` | Observe the expected inventory at the boundary before semantic AST construction. Compare it with the independent syntax expectations. | Each expected occurrence appears once with the correct kind, logical source path, coordinates, and qualified owner. The flow, step number, branch, and `AS` identity agree with the source wherever applicable. The two annotations share a line and have distinct columns and occurrence identities. |
| `AST-AC-002-02` | Verify the baseline export against the construct checks below. After construction and before reconciliation, run separate variants that drop one occurrence, duplicate one occurrence, move one occurrence to a different valid owner or branch, or change one argument, type, literal, or scope. Keep the source fixture and its expected inventory fixed. | The baseline preserves the expected values and ownership. Each mutation produces a structured reconciliation error identifying the affected occurrence and its logical path and coordinates, and blocks successful export. Moving an otherwise identical occurrence and changing only its payload both fail even when the total occurrence count stays the same. |
| `AST-AC-002-03` | Validate the baseline `source_inventory` with the documented schema revision. Compare its identities with the independent syntax expectations and resolve each mapping using the documented rules. Include a declaration used by Scaffgen and a constraint used by POX. | Every expected occurrence has exactly one inventory record. Each mapping resolves to its intended semantic construct and qualified owner, and its coordinates conform to the documented conventions. |

**Semantic preservation checks for `AST-AC-002-02`**

| Construct group | Compare these values with the source syntax |
| --- | --- |
| Declarations and types | Qualified component, interface, and operation identities, parameters, result and error types, and data field names, types, and constraints. |
| Flows and branches | Numbered steps, operations, operands, literals, guards, dependencies, branch identities and order, return values, and exceptional or failure actions. |
| Annotations and traces | Names, arguments, locations, attachments, scopes, `AS` identities, and upstream trace references. Include multiple annotations on one line. |
| Conditions and contracts | Preconditions, typed postconditions, observation or result fields, operators, expected values, ordered cases and guards, outcomes, and explicit entry-point-to-flow mappings. |
| Assumptions, invariants, and models | Conditions, scopes, affected constructs, consequences, and references to relevant models or imports. |

**Subtasks**

| Owner | Scope and deliverable | Criteria |
| --- | --- | --- |
| Parser schema maintainer | Document the supported `source_inventory` schema revision and how a consumer identifies it. Define the occurrence identity fields, line and column bases, range conventions, and how a consumer resolves an inventory record to its semantic construct. Use the logical source paths supplied by `AST-US-001`. | `AST-AC-002-01`, `AST-AC-002-03` |
| Parser maintainer | Build the syntax-derived inventory before conversion. Preserve the required semantic values and ownership, including the audited omissions in step annotations, field constraints, top-level `ENSURE`, and model `FILE` references. Reconcile the inventory before export and deliver the verified records or a source-located diagnostic. | `AST-AC-002-01` through `AST-AC-002-03` |
| Parser test maintainer | Deliver `AST-AT-003` fixtures with independent syntax expectations, schema and mapping checks, and controlled semantic mutations that exercise reconciliation. | `AST-AC-002-01` through `AST-AC-002-03` |

### AST-US-003 Publish one validated AST for the CPC handoff

As a CPC run operator, I want one validated semantic AST and an independently verifiable digest of its delivered bytes so POX and Scaffgen can bind their outputs to the same input.

**Source** [AST-REQ-003](#ast-req-003-publish-one-validated-ast-artifact) · [Existing exact-byte fingerprint story](AST-Provenance-Requirements.md#us-ast-provenance-015--verify-the-exact-exported-ast-artifact) · [CPC parser provenance](../../../../SEED-CPC-Spec/CPC-System/parser/GASD-Parser-AST-Provenance-Requirements.md#fingerprint-of-the-exported-ast)

**Implementation status** In 2.1.11, every validated semantic export carries the full marker and verified inventory. The parser publishes `semantic_ast_sha512` after delivering the AST. [Implementation](#implementation-in-2111) · [2.1.10 audit](#implementation-audit)

| Criterion | Fixture and action | Pass condition |
| --- | --- | --- |
| `AST-AC-003-01` | Run a valid GASD 1.2 CPC fixture with imports. Repeat with a semantic validation error and with an independently injected reconciliation failure. Start each failure run with a fresh output destination. Exercise a syntax-only export with `--no-validate` as a compatibility case. | A valid run publishes one semantic AST after both checks pass. Its complete `semantic_validate` marker has `status` equal to `PASSED` and reports the correct parser and GASD versions. Its `provenance.sources` and verified `source_inventory` satisfy `AST-US-001` and `AST-US-002`. Each failure publishes no successful CPC AST or `PASSED` result for the current run. A syntax-only result is ineligible for the CPC handoff even if the CLI exits zero. [Validation marker shape](AST-Provenance-Requirements.md#provenance-parity-across-ast-output-destinations) · [Syntax-only regression](../../../Impl/tests/acceptance/test_ast_provenance.py#L221) |
| `AST-AC-003-02` | Capture the final JSON bytes at the selected CPC handoff before decoding or reserialization and independently compute SHA-512. Separately exercise digest calculation with two fixed JSON test vectors that differ only by a trailing LF. | The external `semantic_ast_sha512` equals SHA-512 of the final delivered bytes and has 128 lowercase hexadecimal characters. The trailing-LF test vectors have different digests, each correct for its own bytes. When the parser report and CPC record describe the same export, `semantic_validate.semantic_ast_bytes_sha512` in that report equals the CPC digest. On the full export, the embedded marker's byte digest verifies using its documented zeroing rule and the source digests verify against the corresponding GASD captures. [Fingerprint requirements](AST-Provenance-Requirements.md#ast-fingerprints-in-the-parse-report) · [Embedded digest rules](AST-Provenance-Requirements.md#provenance-parity-across-ast-output-destinations) |

**Subtasks**

| Owner | Scope and deliverable | Criteria |
| --- | --- | --- |
| Parser maintainer | Use the complete source provenance and reconciled inventory from the first two stories to gate publication. Deliver one validated semantic AST for a successful CPC input and a diagnostic on either validation or reconciliation failure. | `AST-AC-003-01` |
| CPC integration maintainer | Use the parser report's root `semantic_ast_sha512` to verify the exact exported bytes supplied to POX and Scaffgen. | `AST-AC-003-02` |
| Parser maintainer | Publish `semantic_ast_sha512` after delivering the final JSON bytes to the selected file or stdout. | `AST-AC-003-02` |
| Parser test maintainer | Exercise successful and failed publication and compare the recorded digest with an independent hash. Retain the report and embedded fingerprint regressions. [Provenance tests](../../../Impl/tests/acceptance/test_ast_provenance.py) | `AST-AC-003-01`, `AST-AC-003-02` |

**Handoff** The parser records `semantic_ast_sha512` at the root of the JSON parse report. Verify it against the bytes delivered to the selected file or stdout, before decoding or reserializing. [CPC shared AST input](../../../../SEED-CPC-Spec/CPC-System/scaffgen/Scaffgen-PO-Linking-Requirements.md#inputs-and-generation-modes)

### Story verification

| Verification | Story and criteria | Evidence or required coverage |
| --- | --- | --- |
| `AST-AT-001` | `AST-US-001` · `AST-AC-001-01`, `AST-AC-001-02` | Verify the exact source set, raw-byte digests, and locations for the entry and both levels of imports. [Existing transitive-source test](../../../Impl/tests/acceptance/test_ast_provenance.py#L87) |
| `AST-AT-002` | `AST-US-001` · `AST-AC-001-01`, `AST-AC-001-03` | Verify capture consistency and blocked export for unreadable input. Exercise unresolved imports and path conflicts as additional negative cases. [Existing capture test](../../../Impl/tests/acceptance/test_ast_provenance.py#L102) · [Existing unresolved import test](../../../Impl/tests/acceptance/test_ast_provenance.py#L210) |
| `AST-AT-003` | `AST-US-002` and `AST-US-003` · `AST-AC-002-01`, `AST-AC-002-02`, `AST-AC-002-03`, `AST-AC-003-01` | Use same-line annotations, typed postconditions, and nested failure branches to verify the occurrence inventory and its mappings on success. Inject a loss or change and verify the diagnostic and blocked publication. [Recorded parser behavior](#acceptance-test-results) |
| CPC publication and exact-byte digest | `AST-US-003` · `AST-AC-003-01`, `AST-AC-003-02` | Verify the successful payload, exercise both validation failure paths, and independently hash the final bytes. Reuse `RT-AST-PROVENANCE-015-01` for the trailing-LF test. With an earlier AST at the destination, verify that a failed run publishes no success result or digest for that run. [Existing provenance tests](AST-Provenance-Requirements.md#story-acceptance-and-regression-tests) · [Failed export regression](../../../Impl/tests/acceptance/test_ast_provenance.py#L221) |
