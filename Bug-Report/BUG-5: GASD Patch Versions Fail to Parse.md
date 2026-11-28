# BUG-5 GASD patch versions fail to parse and print duplicate diagnostics

`gasd_parser` 2.1.13 (build `2026-11-26T21:20:25Z`) rejects the `VERSION 1.2.1` header in the GASD 1.2.1 self-definition. The human-readable CLI prints the same syntax error twice for the single file.

## Steps to reproduce

Run the original command from the `General-Agentic-Software-Design-Language` repository root.

```sh
gasd_parser GASD-1.2.1/gasd-1.2.1.gasd
```

This minimal input reproduces the failure from any directory.

```sh
gasd_parser - <<'GASD'
VERSION 1.2.1
CONTEXT: "Version header"
TARGET: "Python3"
TYPE Example: value: String
GASD
```

## Actual behavior

Both commands exit with code `1`. The error points to the second dot on line 1, at zero-based column 11. The CLI prints the failure banner and diagnostic twice while the summary counts one failed file.

```text
ERROR: stdin failed validation
error[SYNTAX]: mismatched input '.' expecting NEWLINE
  --> stdin:1:11
  Token: '.'
```

The minimal input with `VERSION 1.2.0` fails in the same way. With `VERSION 1.2`, it passes and exits `0`. `--no-validate` reproduces the syntax failure and the repeated diagnostic. `--json` records one syntax error and emits no AST.

## Expected behavior

`VERSION 1.2` is a legal two-component header. The GASD 1.2.1 Specification §3 defines `VERSION 1.2` and `VERSION 1.2.0` as equivalent declarations of GASD 1.2.0. It also accepts `VERSION 1.2.1`, which inherits the GASD 1.2 rules. The parser should accept all three headers and preserve the declared version in AST metadata. An actual syntax failure should print one failure banner and one copy of each diagnostic.

## Root cause

1. The lexer tokenizes `1.2.1` as `FLOAT_LITERAL("1.2")`, `DOT`, and `INTEGER("1")`. The `version_number` rule accepts a patch suffix only on its `INTEGER DOT INTEGER` alternative. Once the parser consumes `FLOAT_LITERAL`, the enclosing directive expects a newline. [Lexer rule](../Impl/grammar/GASDLexer.g4#L170) · [Version directive](../Impl/grammar/GASDParser.g4#L47)
2. The CLI prints the syntax report when it skips a failed parse and prints the same stored report again in final result reporting. [Parse failure handling](../Impl/cli.py#L159) · [Final result reporting](../Impl/cli.py#L287)

The semantic checks also compare version strings directly to `"1.2"`. A quoted `VERSION "1.2.1"` passes parsing today, but the parser reports a missing field-annotation `AS` identifier as INFO and exits `0`. The same field under `VERSION 1.2` raises `LINT-011` at ERROR and exits `1`. A grammar fix needs to carry the inherited validation rules through to both patch versions. [Version resolution](../Impl/semantic/VersionResolver.py#L58) · [Lint severity](../Impl/semantic/LintEngine.py#L25)

## Proposed fix

- Make the patch component optional in the version directive and regenerate the ANTLR parser.
- Apply GASD 1.2 validation rules to `1.2.0` and `1.2.1` while retaining the declared version in exported metadata.
- Emit parse diagnostics through the CLI's final reporting pass. Add regression coverage for all three valid headers (`1.2`, `1.2.0`, and `1.2.1`), inherited lint severity, and a malformed header that produces a single syntax diagnostic.
