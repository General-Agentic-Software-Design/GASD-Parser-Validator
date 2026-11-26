# Bug Report: GASD 1.2 field annotations can omit the required `AS` identifier

## Description

`gasd_parser` 2.1.11 accepts a `VERSION 1.2` file with an inline field annotation that omits its `AS` identifier. The CLI exits with code `0`, reports `semantic_validate.status` as `PASSED`, and publishes a semantic AST. GASD 1.2 requires an `AS` identifier on every annotation and classifies its absence as a `LINT-011` error. [Obligation identifiers, §14.6](../GASD/GASD-1.2/GASD_Specification.md#146-obligation-identifiers--as-gasd-12-addition) · [Linting rules, §15](../GASD/GASD-1.2/GASD_Specification.md#15-linting-engine-gasd-12-addition)

### Steps to Reproduce

Save this example as `missing_annotation_alias.gasd`.

```gasd
VERSION 1.2
CONTEXT: "Reproduce missing annotation alias validation"
TARGET: "Go"
NAMESPACE: "example.hello"

TYPE HelloInput:
    name: String @min_length(1)
```

Run the parser from a directory where `ast.json` does not already exist.

```sh
gasd_parser --ast-sem --ast-combine --json --ast-output ast.json missing_annotation_alias.gasd 2>report.json
```

### Actual Behavior

The parser exits with code `0` and reports no errors. Both the field annotation and its `source_inventory` entry contain `"alias": null`. POX 1.1.1 rejects the exported AST with `AST_ENVELOPE_INVALID` and the message `pointer annotation does not match its AS alias` at line 7, column 17.

### Expected Behavior

The parser should exit with a nonzero status, report a `LINT-011` error at `@min_length(1)` on line 7, column 17, and withhold the semantic AST. Changing the field to `name: String @min_length(1) AS HELLO_NAME_MIN` should pass validation and export that identifier.

## Root Cause

`LintEngine.lint_system()` calls `lint_node()` for each resolved type declaration and skips its fields. `LINT-011` only checks the annotations of nodes it visits. During semantic export, `_res_field()` stores field annotations as serialized data in `cpc_fields`, so the export contains the annotation even though the linter skipped it. [LintEngine.py](../Impl/semantic/LintEngine.py#L59) · [SemanticPipeline.py](../Impl/semantic/SemanticPipeline.py#L136)

## Fix Implemented

Version 2.1.12 applies `LINT-011` to authored `TYPE` field annotations during semantic validation. The diagnostic points to the annotation and blocks AST publication for GASD 1.2. For GASD 1.1 and for unversioned files without a CLI override, the diagnostic is informational. [Design](../Design/field_annotation_alias_design.gasd) · [Release notes](../Build/ver-2.1/RELEASE_NOTES_2.1.12.md)

The tests cover semantic validation without export, rejection at both AST destinations, explicit identifiers in the AST and source inventory, multiple annotations on one line, and mixed GASD versions. [Acceptance tests](../Impl/tests/acceptance/test_field_annotation_alias.py) · [Rejection tests](../Impl/tests/negative/test_field_annotation_alias_negative.py)

## Impact

Obelisk's Hello World tutorial can pass GASD validation and then fail during POX extraction. Reporting the missing identifier during parsing would point authors directly to the annotation they need to fix.
