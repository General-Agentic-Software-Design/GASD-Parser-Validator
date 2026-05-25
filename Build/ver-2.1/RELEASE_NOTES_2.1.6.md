# GASD Parser-Validator v2.1.6 Release Notes

**Release Date:** 2026-05-25  
**Build Time:** 2026-05-25T03:59:44Z

## Summary

Version 2.1.6 fixes a critical bug where absolute file paths were leaking into JSON output when using `--no-validate --ast-output` mode.

## Bug Fixes

### Fixed: Absolute Paths in --no-validate --ast-output JSON

**Issue:** When using `gasd_parser --no-validate --ast-output`, the generated JSON contained absolute file paths in the `sourceFile` field instead of relative paths.

**Root Cause:** The `ASTExporter` class (used in `--no-validate` mode) did not implement path relativization logic, while `SemanticASTExporter` (used in semantic mode) did.

**Fix:** Added `relativize_dict()` and `_do_relativize()` methods to `ASTExporter` class to ensure all paths are relativized to the current working directory (CWD) before JSON serialization.

**Files Modified:**
- `Impl/ast/ASTExporter.py` - Added path relativization logic
- `Design/relative_json_paths_design.gasd` - Updated to document both exporters
- `Validation/Regression/relative_json_paths_regression.gasd` - Added RT-PARSER-010-03 test case
- `Impl/tests/regression/test_relative_json_paths_regression.py` - Added `test_no_validate_ast_output_uses_relative_paths()`

**Impact:** All JSON output now uses portable relative paths regardless of which export mode is used, ensuring consistency and preventing absolute path leakage.

## Testing

- All 672 tests pass
- New regression test added: `test_no_validate_ast_output_uses_relative_paths`
- Verified relative path output in both `--ast-sem` and `--no-validate` modes

## Distribution

**Artifacts:**
- `gasd_parser-2.1.6-py3-none-any.whl`
- `gasd_parser-2.1.6.tar.gz`

**Location:** `Build/Installation/dist/`

## Installation

```bash
pip install gasd_parser-2.1.6-py3-none-any.whl
```

## Verification

```bash
gasd_parser --version
# Output: gasd_parser 2.1.6 (built: 2026-05-25T03:59:44Z)
```

## Traceability

- **User Story:** US-PARSER-010 (Universal Relative JSON Paths)
- **Acceptance Criteria:** AC-PARSER-010-01, AC-PARSER-010-02
- **Regression Test:** RT-PARSER-010-03
- **Design:** Design/relative_json_paths_design.gasd
