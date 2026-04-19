# GASD Parser-Validator Installation

Version: 2.1.5

## Prerequisites
- Python 3.10+
- `antlr4-python3-runtime==4.13.1`

## Installation
From this directory, run:
```bash
pip install dist/gasd_parser-2.1.5-py3-none-any.whl
```

## Running the Parser
Once installed, use:
```bash
gasd_parser --ast-sem <file.gasd>
```
Or for JSON output:
```bash
gasd_parser --ast-sem --json <file.gasd>
```
