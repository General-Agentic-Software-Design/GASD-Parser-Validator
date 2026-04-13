# User Story — Semantic Validation Marker in AST

**Story ID:** US-PARSER-008
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want the **Semantic AST JSON output** (generated via `--json --ast-sem`) to include a **validation certificate** (marker),
So that downstream tools can programmatically verify the AST has passed semantic checks and track its origin (version and build time).

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-008-01 | When running with both `--json` and `--ast-sem`, the JSON output MUST include a root-level key `semantic_validate`. |
| AC-PARSER-008-02 | The `semantic_validate` object MUST contain a `status` field set to `"PASSED"` upon successful validation. |
| AC-PARSER-008-03 | The object MUST include `parser_version` containing the current version of the `gasd_parser`.           |
| AC-PARSER-008-04 | The object MUST include `build_time` containing the build-time timestamp of the parser binary/package.   |
| AC-PARSER-008-05 | The object MUST include `validation_time` containing the ISO-8601 timestamp of when validation passed. |
| AC-PARSER-008-06 | If semantic validation fails, the `semantic_validate` marker MUST NOT be encoded as `"PASSED"`.        |

---

### Example Output (Passed)

```json
{
  "semantic_validate": {
    "status": "PASSED",
    "parser_version": "2.1.3",
    "build_time": "2026-04-10T14:30:00Z",
    "validation_time": "2026-04-12T22:15:00Z"
  },
  "nodes": [...]
}
```

### Pre-requisite / Error Example (Failure)

When an external tool (like `pox`) receives an AST that lacks this marker or fails the check, it should reject the input:

```json
{
  "errors": [
    {
      "error_code": "INPUT_NOT_SEMANTIC",
      "message": "[INPUT_NOT_SEMANTIC] Input is a Syntactic AST (missing semantic_pass). at :0:0",
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