# User Story — Exclusive File Output for --ast-output

**Story ID:** US-PARSER-013
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want the parser to **write the AST JSON content exclusively to the specified file** when `--ast-output <output-file>` is provided,
So that stdout remains free of JSON data, enabling clean pipeline composition where downstream tools can consume the file directly without needing to filter or redirect stdout.

---

### Background & Rationale

When `--ast-output <output-file>` is supplied, the current behavior writes the AST JSON to both the specified file **and** stdout. This creates several problems:

1. **Pipeline pollution** — Downstream tools piping stdout receive unexpected JSON mixed with human-readable status messages.
2. **Duplicate I/O** — Writing the same (potentially large) JSON payload twice is wasteful.
3. **Principle of least surprise** — Specifying an explicit output file implies the intent to capture the content there, not on the console.

This story mandates that `--ast-output` acts as an **exclusive redirect**: the JSON content goes to the file only, and stdout is reserved for human-readable status, warnings, or errors.

---

### Acceptance Criteria

| ID               | Criteria                                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC-PARSER-013-01 | When `--ast-output <output-file>` is specified, the complete AST JSON content MUST be written to `<output-file>`.                                |
| AC-PARSER-013-02 | When `--ast-output <output-file>` is specified, the AST JSON content MUST NOT appear on stdout.                                                  |
| AC-PARSER-013-03 | When `--ast-output <output-file>` is specified, non-JSON human-readable output (e.g., validation summary, warnings, errors) MAY still be emitted to stdout/stderr as normal. |
| AC-PARSER-013-04 | When `--ast-output` is NOT specified, the existing default behavior of writing the AST JSON to stdout MUST be preserved (no regression).          |
| AC-PARSER-013-05 | The file written by `--ast-output` MUST be a valid, well-formed JSON document identical in content to what would have been emitted to stdout.     |
| AC-PARSER-013-06 | If the specified `<output-file>` path is not writable (e.g., permission denied, invalid path), the parser MUST exit with a non-zero exit code and emit a clear error message to stderr. |

---

### Acceptance Tests

| Test ID          | Description                                                                                                                                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| AT-PARSER-013-01 | Run `gasd_parser --ast-sem --ast-output out.json valid.gasd` and verify `out.json` contains a valid, complete AST JSON document.                             |
| AT-PARSER-013-02 | Run `gasd_parser --ast-sem --ast-output out.json valid.gasd` and capture stdout; verify stdout does **not** contain any JSON content (no `{`, no AST nodes). |
| AT-PARSER-013-03 | Run `gasd_parser --ast-sem valid.gasd` (without `--ast-output`) and verify the AST JSON is emitted to stdout (existing default behavior preserved).          |
| AT-PARSER-013-04 | Run `gasd_parser --ast-sem --ast-output out.json valid.gasd` and compare the content of `out.json` against the stdout output of `gasd_parser --ast-sem valid.gasd`; verify both are semantically identical JSON. |
| AT-PARSER-013-05 | Run `gasd_parser --ast-sem --ast-output /invalid/path/out.json valid.gasd` and verify the exit code is non-zero and stderr contains an error message indicating the file could not be written. |
| AT-PARSER-013-06 | Run `gasd_parser --ast-sem --json --ast-output out.json valid.gasd` and verify that stdout remains free of AST JSON while `out.json` contains the full output. |

---

### Regression Tests

| Test ID          | Description                                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------------------- |
| RT-PARSER-013-01 | Verify that `--ast-output` combined with `--ast-combine` (multi-file) still writes the aggregated AST exclusively to the file and not to stdout. |
| RT-PARSER-013-02 | Verify that `--ast-output` combined with `--no-validate` still writes the (non-validated) AST exclusively to the file and not to stdout. |
| RT-PARSER-013-03 | Verify that existing workflows using `--ast-sem` without `--ast-output` continue to emit AST JSON to stdout without any behavioral change. |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-013 Exclusive File Output for --ast-output | US-PARSER-013 | AT-PARSER-013-01, AT-PARSER-013-02, AT-PARSER-013-03, AT-PARSER-013-04, AT-PARSER-013-05, AT-PARSER-013-06 | RT-PARSER-013-01, RT-PARSER-013-02, RT-PARSER-013-03 |
