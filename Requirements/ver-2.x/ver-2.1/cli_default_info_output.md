# User Story — CLI Default Info Output

**Story ID:** US-PARSER-011
**Epic:** EPIC-PARSER-001

### User Story

As a **GASD User**,
I want **the `gasd_parser` to display the version and build info when run without any options**,
So that I can immediately see the tool's version details along with the standard usage information, ensuring I am using the correct build.

---

### Acceptance Criteria

| ID               | Criteria                                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| AC-PARSER-011-01 | When `gasd_parser` is executed with zero arguments, the standard output MUST include the program's version number. |
| AC-PARSER-011-02 | When `gasd_parser` is executed with zero arguments, the standard output MUST include the build information (e.g., build timestamp or commit hash). |
| AC-PARSER-011-03 | The version and build information MUST be displayed in addition to the standard usage and help message that currently appears. |

---

### Example Output

```text
GASD-Parser Version: 2.1.3 (Build: 2026-04-10T14:30:00Z)

usage: gasd_parser [-h] [--json] [--ast-sem] [--ast-combine] [--ast-output AST_OUTPUT] [--gasd-ver GASD_VER] [--no-validate] [-v]
                   [path ...]

GASD-Parser: Validation for Agentic Software Design.

...
```

---

### Acceptance Tests

| Test ID          | Description                                                                  |
| ---------------- | ---------------------------------------------------------------------------- |
| AT-PARSER-011-01 | Run `gasd_parser` without any positional arguments or flags and verify the output explicitly includes the version number. |
| AT-PARSER-011-02 | Run `gasd_parser` without any arguments and verify the output explicitly includes the build information. |
| AT-PARSER-011-03 | Run `gasd_parser` without any arguments and confirm the standard usage/help text is still printed alongside the version and build info. |

---

### Regression Tests

| Test ID          | Description                                                    |
| ---------------- | -------------------------------------------------------------- |
| RT-PARSER-011-01 | Verify `gasd_parser -v` or `--version` still function correctly to output the version details. |
| RT-PARSER-011-02 | Verify `gasd_parser -h` or `--help` still displays the standard help message (with or without the new header, depending on implementation). |

---

### Requirements Traceability Matrix

| Requirement | User Story | Acceptance Test | Regression Test |
| :--- | :--- | :--- | :--- |
| REQ-011 Default Version and Build Info Output | US-PARSER-011 | AT-PARSER-011-01, AT-PARSER-011-02, AT-PARSER-011-03 | RT-PARSER-011-01, RT-PARSER-011-02 |
