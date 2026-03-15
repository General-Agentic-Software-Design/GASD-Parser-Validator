# GASD Parser & Validator

Official implementation of the GASD 1.1 specification language (Version 1.2.0).

## Installation

```bash
pip install .
```

## Uninstallation

```bash
pip uninstall gasd-parser
```

## Usage

### Validate a file

```bash
gasd-parser path/to/file.gasd
```

### Validate a directory (recursive)

```bash
gasd-parser path/to/dir/
```

### Export Syntactic AST to JSON

```bash
gasd-parser --ast path/to/file.gasd
```

### Export Semantic AST to JSON

```bash
gasd-parser --ast-sem path/to/file.gasd
```

### Export to specific file

```bash
gasd-parser --ast-sem --ast-output output.json path/to/file.gasd
```

### Combine multiple ASTs (Syntactic or Semantic)

```bash
gasd-parser --ast-sem --ast-combine path/to/dir/ --ast-output combined.json
```

### JSON Reporting

```bash
gasd-parser path/to/file.gasd --json
```

## Options

- `--json`: Output results in machine-readable JSON format.
- `--ast`: Extract and output the Syntactic AST in JSON format.
- `--ast-sem`: Extract and output the Semantic AST in JSON format.
- `--ast-output <path>`: Path to save the extracted AST JSON file.
- `--ast-combine`: Combine multiple ASTs into a single JSON output.
- `--no-validate`: Skip semantic validation, only check syntax.
