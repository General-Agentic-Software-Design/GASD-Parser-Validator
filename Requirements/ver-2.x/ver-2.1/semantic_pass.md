# User Story — Semantic Validation Marker in AST

**Story ID:** US-PARSER-008
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want each validated **Semantic AST JSON export** to include a **validation certificate** (marker),
So that downstream tools can programmatically verify the AST has passed semantic checks and track its origin (version and build time).

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-008-01 | A validated semantic AST written to stdout or a file MUST include a root-level key `semantic_validate`. |
| AC-PARSER-008-02 | The `semantic_validate` object MUST contain a `status` field set to `"PASSED"` upon successful validation. |
| AC-PARSER-008-03 | The object MUST include `parser_version` containing the current version of the `gasd_parser`.           |
| AC-PARSER-008-04 | The object MUST include `build_time` containing the build-time timestamp of the parser binary/package.   |
| AC-PARSER-008-05 | The object MUST include `validation_time` containing the ISO-8601 timestamp of when validation passed. |
| AC-PARSER-008-06 | If semantic validation fails, the `semantic_validate` marker MUST NOT be encoded as `"PASSED"`.        |

---

### Example Output (Excerpt)

```json
{
  "kind": "SemanticSystem",
  "semantic_validate": {
    "status": "PASSED",
    "parser_version": "2.1.11",
    "build_time": "2026-11-25T23:01:45Z",
    "validation_time": "2026-11-26T00:00:00Z",
    "gasd_file_version": "1.2"
  }
}
```

The full marker also carries three fingerprint fields. `PASSED` is published in a semantic AST after both validation and source reconciliation succeed. [Complete marker](AST-Provenance-Requirements.md#provenance-parity-across-ast-output-destinations)

### Pre-requisite / Error Example (Failure)

When an external tool (like `pox`) receives an AST that lacks this marker or fails the check, it should reject the input:

```json
{
  "errors": [
    {
      "error_code": "INPUT_NOT_SEMANTIC",
      "message": "[INPUT_NOT_SEMANTIC] Input is a syntactic AST without a semantic_validate marker.",
      "file": "stdin",
      "line": 0,
      "column": 0,
      "severity": "FATAL"
    }
  ]
}
```

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-008-01 | Run `gasd_parser --json --ast-sem valid.gasd` and verify JSON contains `semantic_validate`. |
| AT-PARSER-008-02 | Verify `parser_version` and `build_time` match current system metadata.       |
| AT-PARSER-008-03 | Verify `validation_time` reflects the current execution time.                |
| AT-PARSER-008-04 | Run with `--no-validate` and verify the `semantic_validate` status is NOT `"PASSED"`. |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-008-01 | Ensure existing AST consumers do not crash due to the additional root-level key. |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-008 Validation Marker | US-PARSER-008 | AT-PARSER-008-01, AT-PARSER-008-02, AT-PARSER-008-03, AT-PARSER-008-04 | RT-PARSER-008-01 |
