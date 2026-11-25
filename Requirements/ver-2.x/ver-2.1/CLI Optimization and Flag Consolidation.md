# User Story — CLI Optimization and Flag Consolidation

**Story ID:** US-PARSER-007
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Developer**,
I want to **remove the redundant --ast flag and consolidate validation controls under --ast-sem**,
So that the CLI interface is simpler and more predictable for cross-file designs.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-007-01 | The `--ast` flag is removed and treated as an unknown option (no legacy support).                      |
| AC-PARSER-007-02 | Semantic validation is enabled by default. Request AST output with `--json`, `--ast-output`, or `--ast-combine`. |
| AC-PARSER-007-03 | Validated semantic exports apply full semantic validation and reconcile the exported model with its sources. |
| AC-PARSER-007-04 | The `--no-validate` flag skips semantic validation even when `--ast-sem` is specified.                |
| AC-PARSER-007-05 | When `--gasd-ver` is absent, the parser MUST interpret each file according to its internal `VERSION` directive. |

---

### CLI Option Interaction Matrix

| Flag A | Flag B | Behavior / Expected Result |
| :--- | :--- | :--- |
| **(No Flags)** | | Full semantic validation on all files. Console summary output. |
| **--ast-sem** | | Full semantic validation with a console summary, matching the default. |
| **--no-validate** | | Syntax parsing only. Skips all semantic validation checks. |
| **--json** | | Outputs the AST JSON to stdout and the machine-readable validation report to stderr. |
| **--version** | | Displays program version and exits immediately. |
| **--help (-h)** | | Displays help message and exits immediately. |
| **--ast** | | **[REMOVED]** Treated as an unknown argument (no legacy support). |
| **--json** | **--no-validate** | Writes a syntactic AST to stdout and a JSON report without an AST digest to stderr. |
| **--ast-output `path`** | | Saves the verified Semantic AST to the file and reports the exact-byte digest on stderr. |
| **--ast-output `path`** | **--json** | Saves the verified Semantic AST to the file and writes a JSON report with `semantic_ast_sha512` to stderr. |
| **--ast-combine** | | Used with multiple files to aggregate ASTs into a single output object. |
| **--gasd-ver 1.1** | | Overrides internal versioning to validate against GASD 1.1 spec. |
| **--gasd-ver 1.2** | | Overrides internal versioning to validate against GASD 1.2 spec. |

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-007-01 | Running with `--ast` returns an error (unknown argument, no legacy support). |
| AT-PARSER-007-02 | Running with `--json --no-validate` produces a syntactic AST without a verified inventory. |
| AT-PARSER-007-03 | Running with `--ast-sem` (default validation) performs full semantic checks. |
| AT-PARSER-007-04 | Running with `--json` alone produces a source-checked semantic AST. |
| AT-PARSER-007-05 | In a multi-file run without `--gasd-ver`, verify each file is validated against its specified version (1.1 vs 1.2). |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-007-01 | Ensure `--json` and `--ast-output` still work with `--ast-sem`. |

---

### Requirements Traceability Matrix

| Requirement                 | User Story    | Acceptance Test  | Regression Test  |
| --------------------------- | ------------- | ---------------- | ---------------- |
| REQ-007 CLI Flag Consolidation | US-PARSER-007 | AT-PARSER-007-01, AT-PARSER-007-02, AT-PARSER-007-03, AT-PARSER-007-04, AT-PARSER-007-05 | RT-PARSER-007-01 |

---
