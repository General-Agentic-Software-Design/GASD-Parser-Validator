# GASD Parser 2.1.11

Validated semantic AST exports now verify source occurrences automatically. The parser captures each input and resolved import once, checks the output against the authored constructs, and blocks publication if a source is unavailable or reconciliation fails.

```bash
gasd_parser --ast-output ast.json input.gasd
gasd_parser --json --ast-output ast.json input.gasd 2> parse-report.json
```

Both commands write an AST with `provenance.sources`, the verified `source_inventory` at revision 1, and a `PASSED` validation marker. The first command prints the exact AST digest in the human-readable report. The second puts it in `semantic_ast_sha512` at the root of the JSON report. Hash the delivered file as-is to verify that value. The `--json` option also supports streaming the AST to stdout when no file destination is supplied. [AST requirements](../../Requirements/ver-2.x/ver-2.1/GASD_Parser_AST_Requirements.md) · [CLI usage](../../README.md#usage)

Use `--no-validate` for syntax-only output. These exports omit the verified inventory and the exact-byte handoff digest. [AST provenance requirements](../../Requirements/ver-2.x/ver-2.1/AST-Provenance-Requirements.md)

Install 2.1.11 from the distribution for Python 3.9 or later. [Installation](../Installation/README.md) · [Wheel](../Installation/dist/gasd_parser-2.1.11-py3-none-any.whl) · [Source distribution](../Installation/dist/gasd_parser-2.1.11.tar.gz)
