# GASD Parser Project — Version 1.1 User Stories

This document defines new user stories for GASD 1.1, focusing on AST extraction and enhanced CLI capabilities.

## Epic

**EPIC-PARSER-001**
Build a **deterministic parser for the GASD 1.1 specification language** using ANTLR that acts as the **canonical validator and interpreter of GASD 1.1 specification files**.

---

# User Story 7 — AST Extraction and JSON Output

**Story ID:** US-PARSER-007
**Epic:** EPIC-PARSER-001

### User Story

As a **developer**,
I want to **extract the AST from GASD files once they are parsed**,
So that **I can use the structured data to generate other files or perform external analysis**.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-007-01 | AST extraction is performed ONLY after successful semantic validation.                                 |
| AC-PARSER-007-02 | AST extraction is optional and must be enabled via a command-line option (e.g., `--ast`).              |
| AC-PARSER-007-03 | The output format for the extracted AST is JSON.                                                       |
| AC-PARSER-007-04 | The default behavior is to print the JSON AST to the console (STDOUT).                                |
| AC-PARSER-007-05 | The CLI supports specifying an output file for the AST (e.g., `--ast-output <path>`).                  |
| AC-PARSER-007-06 | When processing multiple files, the behavior (one JSON per file vs. combined) is controlled by a command-line option (e.g., `--ast-combine`). |
| AC-PARSER-007-07 | The extracted AST structure strictly follows the hierarchy defined in `Design/ast_design.gasd`.        |
| AC-PARSER-007-08 | JSON output is pretty-printed with standard indentation (e.g., 2 or 4 spaces) for readability.         |
| AC-PARSER-007-09 | The parser handles I/O errors (e.g., permission denied, invalid path) gracefully with clear error messages. |
| AC-PARSER-007-10 | Source location metadata (line, column) for all nodes is included in the JSON output.                  |
| AC-PARSER-007-11 | The addition of AST extraction features MUST NOT break any existing CLI commands or validation logic.  |
| AC-PARSER-007-12 | All existing parsers, validators, and utility tests must pass without modification to their expected results. |

---

### Acceptance Tests

| Test ID          | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| AT-PARSER-007-01 | Running the parser with `--ast` on a valid file prints valid JSON to the console. |
| AT-PARSER-007-02 | Running with `--ast --ast-output out.json` saves the AST to the specified file. |
| AT-PARSER-007-03 | AST is NOT produced if the input file fails semantic validation.            |
| AT-PARSER-007-04 | Running with multiple files and NO `--ast-combine` produces separate output indicators/files. |
| AT-PARSER-007-05 | Running with multiple files and `--ast-combine` produces a single JSON array or object. |
| AT-PARSER-007-06 | Providing an invalid path to `--ast-output` returns a specific I/O error message. |
| AT-PARSER-007-07 | Verifying that all nodes in the JSON output contain `line` and `column` fields. |
| AT-PARSER-007-08 | Verifying that the JSON output is valid against the AST design schema mapping. |

---

### Regression Tests

| Test ID          | Description                                                                 |
| ---------------- | --------------------------------------------------------------------------- |
| RT-PARSER-007-01 | Enabling AST extraction does not affect the standard validation output or exit codes. |
| RT-PARSER-007-02 | Parser performance remains within acceptable limits (e.g., < 10% overhead) when AST extraction is enabled. |
| RT-PARSER-007-03 | The `--help` command correctly lists and describes `--ast`, `--ast-output`, and `--ast-combine`. |
| RT-PARSER-007-04 | Special characters (UTF-8) in GASD strings are correctly escaped and preserved in the JSON AST. |
| RT-PARSER-007-05 | Version reporting (`--version`) remains unchanged and accurate.             |
| RT-PARSER-007-06 | Execution of existing test suites (e.g., `pytest`, `npm test`) shows 100% pass rate for all legacy features. |
| RT-PARSER-007-07 | Valid historical GASD files in `Ref-Specs` continue to parse correctly without requiring AST flags. |

---

# Requirements Traceability Matrix

| Requirement                 | User Story    | Acceptance Test  | Regression Test  |
| --------------------------- | ------------- | ---------------- | ---------------- |
| REQ-007 AST Extraction      | US-PARSER-007 | AT-PARSER-007-01 | RT-PARSER-007-01 |
| REQ-008 JSON Output Support | US-PARSER-007 | AT-PARSER-007-02 | RT-PARSER-007-02 |
| REQ-009 CLI Output Control  | US-PARSER-007 | AT-PARSER-007-05 | RT-PARSER-007-03 |
