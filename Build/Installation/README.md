# GASD Parser-Validator Installation

Version 2.1.10

## Prerequisites

- Python 3.9+
- `antlr4-python3-runtime==4.13.1`

## Installation
From this directory, run:
```bash
python3 -m pip install dist/gasd_parser-2.1.10-py3-none-any.whl
```

## Running the Parser
Once installed, use:
```bash
gasd_parser --ast-sem <file.gasd>
```
To write the AST as JSON on stdout:
```bash
gasd_parser --json file.gasd > ast.json
```

To write the same AST format directly to a file and capture the JSON validation report on stderr:
```bash
gasd_parser --json --ast-output ast.json file.gasd 2> parse-report.json
```

Successful semantic exports list the captured source digests in `provenance.sources`. The JSON report records both AST fingerprints and the content rules version under `semantic_validate`. Validated GASD 1.2 ASTs carry these fields in the validation marker for both output destinations.
