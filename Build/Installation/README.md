# GASD Parser-Validator Installation

Version 2.1.12

## Prerequisites

- Python 3.9+
- `antlr4-python3-runtime==4.13.1`

## Installation
From this directory, run:
```bash
python3 -m pip install dist/gasd_parser-2.1.12-py3-none-any.whl
```

## Running the Parser
Once installed, use:
```bash
gasd_parser file.gasd
```
To write the AST as JSON on stdout:
```bash
gasd_parser --json file.gasd > ast.json
```

To write the same AST format directly to a file and capture the JSON validation report on stderr:
```bash
gasd_parser --json --ast-output ast.json file.gasd 2> parse-report.json
```

Source reconciliation runs automatically for every validated semantic export. The AST includes `provenance.sources`, the verified `source_inventory`, and a `PASSED` validation marker. The JSON report's root `semantic_ast_sha512` is the SHA-512 digest of every byte written to `ast.json`. The `semantic_validate` object in the JSON report also carries the exact-byte and semantic-content fingerprints.

Omit `--json` to get a human-readable report with the same exact-byte digest on stderr.

```bash
gasd_parser --ast-output ast.json file.gasd
```

Use `gasd_parser --version` to check the installed version and build timestamp. [Release notes](../ver-2.1/RELEASE_NOTES_2.1.12.md) · [AST export requirements](../../Requirements/ver-2.x/ver-2.1/GASD_Parser_AST_Requirements.md)
