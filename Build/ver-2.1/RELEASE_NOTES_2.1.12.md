# GASD Parser 2.1.12

Semantic validation now reports `LINT-011` at any `TYPE` field annotation that omits its `AS` identifier in GASD 1.2. The error blocks AST publication. The check also applies when selecting `--gasd-ver 1.2`. GASD 1.1 and unversioned files without a CLI override receive an informational diagnostic for these field annotations. [BUG-3](<../../Bug-Report/BUG-3: Missing AS Validation on GASD 1.2 Field Annotations.md>)

Export a validated semantic AST to a file or stream it to stdout.

```sh
gasd_parser --json --ast-output ast.json input.gasd 2> parse-report.json
gasd_parser --json input.gasd > ast.json 2> parse-report.json
```

Both exports verify authored source occurrences and report the SHA-512 digest of the delivered AST bytes in `semantic_ast_sha512`. [Installation guide](../Installation/README.md)

Install 2.1.12 on Python 3.9 or later. [Wheel](../Installation/dist/gasd_parser-2.1.12-py3-none-any.whl) · [Source distribution](../Installation/dist/gasd_parser-2.1.12.tar.gz)
