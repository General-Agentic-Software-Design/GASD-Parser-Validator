# GASD Parser & Validator

Official implementation of the GASD 1.1 specification language.

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

### Export AST to JSON

```bash
gasd-parser --ast path/to/file.gasd
```

### Combine multiple ASTs

```bash
gasd-parser --ast-combine path/to/file1.gasd path/to/file2.gasd
```
