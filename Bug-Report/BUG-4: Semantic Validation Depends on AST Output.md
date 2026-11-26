# BUG-4 Semantic Validation Depends on AST Output

`gasd_parser` 2.1.12 (build `2026-11-26T03:27:26Z`) reports a successful validation for the GASD 1.2 specification with plain `--ast-sem`. Requesting the semantic AST on stdout or in a file makes the same input fail. This lets a validation-only command return exit code `0` for an input the same parser rejects during export.

## Steps to Reproduce

Run these commands from the repository root. Use a fresh path for `ast.json`.

```sh
spec=GASDSpecs/GASD-1.2/gasd-1.2.0.gasd
gasd_parser --ast-sem "$spec"
gasd_parser --ast-sem --ast-output ast.json "$spec"
gasd_parser --ast-sem --json "$spec"
```

## Actual Behavior

| Options | Exit code | Result |
| --- | --- | --- |
| `--ast-sem` | `0` | Reports `OK Passed`. |
| `--ast-sem --ast-output ast.json` | `1` | Reports `Annotation @format is not allowed in scope STEP` and withholds the AST file. |
| `--ast-sem --json` | `1` | Reports the same error, with `success: false` and `semantic_validate.status: "FAILED"` on stderr. Stdout is empty. |

Both export modes report the error at line 1, column 1. The annotation is on the `VALIDATE` step at line 565. [GASD 1.2 specification](../GASDSpecs/GASD-1.2/gasd-1.2.0.gasd#L565)

## Expected Behavior

All three invocations should run the same semantic checks, including scope checks on flow-step annotations. Under the current annotation registry, this input should exit with code `1` in all three invocations and identify the `@format` annotation on line 565. Export requests should continue to verify the AST against its sources before publishing it. [Annotation registry](../Impl/semantic/AnnotationRegistry.py#L53) · [AST export requirements](../Requirements/ver-2.x/ver-2.1/GASD_Parser_AST_Requirements.md#ast-req-003-publish-one-validated-ast-artifact)

## Root Cause

In 2.1.12, the CLI ran the semantic pipeline for all three invocations and passed `cpc=True` only for AST exports. The syntactic AST contained the inline annotation in both modes. `_res_step()` resolves and validates flow-step annotations when `cpc=True`, so the scope check ran for both export commands and was skipped for plain `--ast-sem`. [Flow-step annotation resolution](../Impl/semantic/SemanticPipeline.py#L276)

## Fix Implemented

Version 2.1.13 builds the same semantic model and resolves readable imports for validation-only and export runs. All three commands above exit `1` and report one `@format` scope error at line 565, column 38. Source reconciliation still gates AST publication. The regression tests also cover nested steps, imported sources, and syntax-only runs. [Design](../Design/semantic_validation_output_parity_design.gasd) · [Tests](../Impl/tests/acceptance/test_semantic_validation_output_parity.py) · [Release notes](../Build/ver-2.1/RELEASE_NOTES_2.1.13.md)
