# GASD Parser 2.1.14

The parser accepts `VERSION 1.2`, `VERSION 1.2.0`, and `VERSION 1.2.1`. All three use GASD 1.2 validation rules, including the `LINT-011` error for a field annotation missing an `AS` identifier. Both semantic AST version fields preserve the declared version. A syntax failure produces one CLI banner per input and one copy of each diagnostic. [BUG-5](<../../Bug-Report/BUG-5: GASD Patch Versions Fail to Parse.md>)

Export a validated semantic AST to a file or stream it to stdout.

```sh
gasd_parser --json --ast-output ast.json input.gasd 2> parse-report.json
gasd_parser --json input.gasd > ast.json 2> parse-report.json
```

Both export modes verify source occurrences and report the SHA-512 digest of the delivered bytes in `semantic_ast_sha512`. [Installation guide](../Installation/README.md)

Install 2.1.14 on Python 3.9 or later. [Wheel](../Installation/dist/gasd_parser-2.1.14-py3-none-any.whl) · [Source distribution](../Installation/dist/gasd_parser-2.1.14.tar.gz)
