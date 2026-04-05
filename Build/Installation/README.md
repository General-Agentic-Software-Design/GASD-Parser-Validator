# GASD Parser & Validator

Official implementation of the GASD 1.2 specification language (Version 2.1.0).

## Installation

From the wheel (recommended):

```bash
pip3 install gasd_parser-2.1.0-py3-none-any.whl
```

Or from the source distribution:

```bash
pip3 install gasd_parser-2.1.0.tar.gz
```

## Uninstallation

```bash
pip3 uninstall gasd-parser
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

### Export Semantic AST to JSON (default mode)

```bash
gasd-parser --ast-sem path/to/file.gasd
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
- `--ast-sem`: Extract and output the Semantic AST in JSON format (default mode).
- `--no-validate`: Skip semantic validation, only check syntax.
- `--ast-output <path>`: Path to save the extracted AST JSON file.
- `--ast-combine`: Combine multiple ASTs into a single JSON output.
- `--json`: Output results in machine-readable JSON format.
- `--gasd-ver <version>`: Specify the authoritative GASD version (1.1 or 1.2).
- `--version`: Show the version and build time.

## Verification

To verify the installation and build time:

```bash
gasd-parser --version
```

Output should look like: `gasd-parser 2.1.0 (built: 2026-04-05T00:00:00Z)`
