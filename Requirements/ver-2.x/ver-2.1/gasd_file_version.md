# User Story — GASD File Version in Semantic AST

**Story ID:** US-PARSER-009
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want the **Semantic AST JSON output** (generated via `--json --ast-sem`) to include the **GASD file version** explicitly,
So that downstream tools can conditionally adjust validation and execution logic based on the format version, or flag the format as "unknown" to prompt human inspection.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-009-01 | The Semantic AST JSON document MUST include a key `gasd_file_version` within the `semantic_validate` object. |
| AC-PARSER-009-02 | If the source `.gasd` file specifies a valid GASD version, the `gasd_file_version` MUST evaluate to the specified version string (e.g., `"1.2"`). |
| AC-PARSER-009-03 | If the source `.gasd` file does NOT specify a GASD version, the `gasd_file_version` MUST evaluate to the literal string `"unknown"`. |
| AC-PARSER-009-04 | The extraction of the file version MUST conform to the semantic rules for identifying version directives within the GASD file format. |

---

### Example Output (With Version Specified)

```json
{
  "semantic_validate": {
    "status": "PASSED",
    "parser_version": "2.1.3",
    "build_time": "2026-04-10T14:30:00Z",
    "validation_time": "2026-04-12T22:15:00Z",
    "gasd_file_version": "1.2"
  },
  "nodes": [...]
}
```

### Example Output (Without Version Specified)

```json
{
  "semantic_validate": {
    "status": "PASSED",
    "parser_version": "2.1.3",
    "build_time": "2026-04-10T14:30:00Z",
    "validation_time": "2026-04-12T22:15:00Z",
    "gasd_file_version": "unknown"
  },
  "nodes": [...]
}
```

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-009-01 | Parse a GASD file containing an explicit version declaration and verify `gasd_file_version` maps to the correct string representation in the AST JSON output. |
| AT-PARSER-009-02 | Parse a GASD file that lacks a version declaration and verify `gasd_file_version` evaluates precisely to `"unknown"` in the AST JSON output. |
| AT-PARSER-009-03 | Execute parser logic against malformed or partially formed `.gasd` files lacking version directives to confirm they still emit `"unknown"` under error-containment modes. |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-009-01 | Verify AST exporter does not crash when encountering legacy `.gasd` files dating back prior to version inclusion specifications. |
| RT-PARSER-009-02 | Ensure existing AST consumers do not fail deserialization due to the new key being present within the `semantic_validate` object. |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-009 GASD File Versioning Metadata | US-PARSER-009 | AT-PARSER-009-01, AT-PARSER-009-02, AT-PARSER-009-03 | RT-PARSER-009-01, RT-PARSER-009-02 |
