# GASD Parser 2.1.13

Validation-only runs and semantic AST exports now use the same semantic checks. Scope and argument errors point to the annotation in its source file, including in imported files. Plain `--ast-sem`, `--json`, and `--ast-output` all reject `@format` attached to a `VALIDATE` flow step. [BUG-4](<../../Bug-Report/BUG-4: Semantic Validation Depends on AST Output.md>)

Export a validated semantic AST to a file or stream it to stdout.

```sh
gasd_parser --json --ast-output ast.json input.gasd 2> parse-report.json
gasd_parser --json input.gasd > ast.json 2> parse-report.json
```

Both exports verify authored source occurrences and report the SHA-512 digest of the delivered AST bytes in `semantic_ast_sha512`. [Installation guide](../Installation/README.md)

Install 2.1.13 on Python 3.9 or later. [Wheel](../Installation/dist/gasd_parser-2.1.13-py3-none-any.whl) · [Source distribution](../Installation/dist/gasd_parser-2.1.13.tar.gz)
