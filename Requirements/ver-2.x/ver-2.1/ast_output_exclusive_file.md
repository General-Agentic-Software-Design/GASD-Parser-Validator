# User Story — Exclusive File Output for --ast-output

**Story ID:** US-PARSER-013
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want `--json` on stdout and `--ast-output <output-file>` to deliver the same AST JSON format and content,
So that downstream tools can consume either destination with the same code.

---

### Background & Rationale

Use one AST serializer for stdout and file export. A semantic export is a top-level `SemanticSystem` with its validation marker when applicable. An export with `--no-validate` uses the syntactic AST format. When `--ast-output` is supplied, it takes precedence over the stdout destination. The machine-readable validation report requested by `--json` goes to stderr.

Destination parity applies to the entire serialized AST for the same input and validation state. Independent runs can produce different generated node UUIDs and validation timestamps. If parsing produces no AST, stdout stays empty and the destination file is left untouched.

---

### Acceptance Criteria

| ID               | Criteria                                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-PARSER-013-01 | When `--ast-output <output-file>` is specified, the complete AST JSON content MUST be written to `<output-file>`.                                |
| AC-PARSER-013-02 | When `--ast-output <output-file>` is specified, the AST JSON content MUST NOT appear on stdout.                                                  |
| AC-PARSER-013-03 | With `--json`, the validation report goes to stderr. With neither JSON nor AST export requested, the existing human-readable reporting applies. |
| AC-PARSER-013-04 | With `--json` and no `--ast-output`, stdout contains the AST JSON when an AST is available. |
| AC-PARSER-013-05 | Both destinations MUST receive the same complete JSON serialization, including encoding, formatting, paths, metadata, and any validation marker. |
| AC-PARSER-013-06 | If the specified `<output-file>` path is not writable (e.g., permission denied, invalid path), the parser MUST exit with a non-zero exit code and emit a clear error message to stderr. |

---

### Acceptance Tests

| Test ID          | Description                                                                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| AT-PARSER-013-01 | Run `gasd_parser --ast-sem --ast-output out.json valid.gasd` and verify `out.json` contains a valid, complete AST JSON document.                             |
| AT-PARSER-013-02 | Run `gasd_parser --ast-sem --ast-output out.json valid.gasd` and capture stdout; verify stdout does **not** contain any JSON content (no `{`, no AST nodes). |
| AT-PARSER-013-03 | Run `gasd_parser --json valid.gasd` and verify stdout contains the top-level AST and stderr contains the JSON validation report. |
| AT-PARSER-013-04 | Run `gasd_parser --json valid.gasd` and `gasd_parser --json --ast-output out.json valid.gasd`. Compare the complete JSON documents, accounting for per-run UUIDs and validation timestamps. With those values fixed, compare the bytes. |
| AT-PARSER-013-05 | Run `gasd_parser --ast-sem --ast-output /invalid/path/out.json valid.gasd` and verify the exit code is non-zero and stderr contains an error message indicating the file could not be written. |
| AT-PARSER-013-06 | Run `gasd_parser --json --ast-output out.json valid.gasd` and verify that stdout is empty, `out.json` contains the full AST, and stderr carries the validation report. |

---

### Regression Tests

| Test ID          | Description                                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| RT-PARSER-013-01 | Verify stdout and file output contain the same combined AST for multiple inputs. |
| RT-PARSER-013-02 | Verify both destinations receive the same syntactic AST with `--no-validate`. |
| RT-PARSER-013-03 | Verify the `--json` stdout path also works for GASD read from stdin. |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-013 Exclusive File Output for --ast-output | US-PARSER-013 | AT-PARSER-013-01, AT-PARSER-013-02, AT-PARSER-013-03, AT-PARSER-013-04, AT-PARSER-013-05, AT-PARSER-013-06 | RT-PARSER-013-01, RT-PARSER-013-02, RT-PARSER-013-03 |
