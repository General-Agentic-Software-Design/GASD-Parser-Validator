# User Story — Relative SourceMap Paths in Semantic AST

**Story ID:** US-PARSER-010
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD Tooling Integrator**,
I want the **Semantic AST JSON sourceMap** (generated via `--json --ast-sem`) to use **relative file paths** instead of absolute paths,
So that the generated AST files are portable across different environments and build systems without revealing internal file system structures.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-010-01 | Every `sourceMap` object in the Semantic AST JSON MUST use a path relative to the Current Working Directory (CWD) for the `file` field. |
| AC-PARSER-010-02 | Absolute file paths MUST NOT be encoded in the `sourceMap.file` field under any circumstances.        |
| AC-PARSER-010-03 | The path resolution MUST handle cross-platform directory separators correctly, standardizing on forward slashes `/`. |
| AC-PARSER-010-04 | If a file is located in a parent directory of the CWD, it MUST use the `../` notation to maintain relativity. |
| AC-PARSER-010-05 | For stdin or virtual files, the `file` field MUST continue to use the designated identifier (e.g., `"stdin"`). |
| AC-PARSER-010-06 | The JSON structural elements (dictionary keys and list elements) MUST NOT contain absolute paths; any absolute path found during serialization MUST be relativized to the CWD. |

---

### Example Output

```json
{
  "nodes": [
    {
      "sourceMap": {
        "file": "specs/feature_a.gasd",
        "line": 15,
        "column": 1
      }
    },
    {
      "sourceMap": {
        "file": "../common/base.gasd",
        "line": 42,
        "column": 1
      }
    }
  ]
}
```

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-010-01 | Run `gasd_parser --json --ast-sem test.gasd` within its directory and verify `file` is `"test.gasd"`. |
| AT-PARSER-010-02 | Run `gasd_parser --json --ast-sem subdir/test.gasd` from the parent and verify `file` is `"subdir/test.gasd"`. |
| AT-PARSER-010-03 | Run from a subdirectory (`cd subdir && gasd_parser --json --ast-sem ../test.gasd`) and verify `file` is `"../test.gasd"`. |
| AT-PARSER-010-04 | Verify that on Windows, paths like `subdir\test.gasd` are converted to `subdir/test.gasd` in the JSON output. |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-010-01 | Ensure that standard JSON output (without `--ast-sem`) also adopts relative paths to maintain consistency across the CLI. |
| RT-PARSER-010-02 | Verify that absolute paths provided as CLI arguments are correctly relativized in the final AST output. |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-010 Relative Source Mapping | US-PARSER-010 | AT-PARSER-010-01, AT-PARSER-010-02, AT-PARSER-010-03, AT-PARSER-010-04 | RT-PARSER-010-01, RT-PARSER-010-02 |
