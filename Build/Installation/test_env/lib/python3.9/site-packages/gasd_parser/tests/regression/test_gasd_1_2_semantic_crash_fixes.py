"""
Regression tests for GASD 1.2 semantic crash fixes.

These tests use file-based fixtures validated through the CLI pipeline,
which correctly handles the indentation lexer's INDENT/DEDENT token generation.

Bug categories covered:
  RT-SEM-CRASH-001: _signatures_match null safety (AttributeError on missing typeRef/baseType)
  RT-SEM-CRASH-002: Labeled type visitor null safety (List/Map/Optional type mapping)
  RT-SEM-CRASH-003: Field alias parsing (AS on TYPE fields)
  RT-SEM-CRASH-004: LINT-001 enforcement for ACHIEVE inside ON_ERROR blocks
  RT-SEM-CRASH-005: CONSTRAINT inline string parsing
  RT-SEM-CRASH-006: Missing custom type declaration detection (UnknownType)
  RT-SEM-CRASH-007: ASSUMPTION annotation placement (block-level vs header)
  RT-SEM-CRASH-008: CONTRACT structure validation (BEHAVIORS/CASE/POSTCONDITION)
"""
import os
import subprocess
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FIXTURE_DIR = os.path.join(PROJECT_ROOT, "Specs", "tests", "regression")
PYTHON_PATH = os.path.join(PROJECT_ROOT, "Build", "Installation")


def run_gasd_validator(*gasd_files, expect_pass=True):
    """Run the GASD CLI validator on the given files and return (returncode, stdout, stderr)."""
    cmd = ["python3", "-m", "gasd_parser", "--ast-sem"] + list(gasd_files)
    env = os.environ.copy()
    env["PYTHONPATH"] = PYTHON_PATH
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=PROJECT_ROOT)
    combined = result.stdout + result.stderr
    if expect_pass:
        assert result.returncode == 0, (
            f"Expected validation to pass but got exit code {result.returncode}.\n"
            f"Output:\n{combined}"
        )
    return result.returncode, combined


def fixture(name):
    """Return the absolute path to a regression fixture file."""
    return os.path.join(FIXTURE_DIR, name)


# ===================================================================
# RT-SEM-CRASH-001: _signatures_match null safety
# Previously caused AttributeError when typeRef or baseType was None
# ===================================================================

def test_rt_sem_crash_001_signatures_null_safety():
    """Pipeline must not crash with AttributeError on custom types in method signatures."""
    run_gasd_validator(fixture("rt_sem_crash_001_signatures_null_safety.gasd"))


# ===================================================================
# RT-SEM-CRASH-002: Labeled type visitors produce non-None types
# Previously, visitType returned None for List/Map/Optional
# ===================================================================

def test_rt_sem_crash_002_labeled_type_visitors():
    """List<T>, Map<K,V>, Optional<T> fields must produce valid types, not None."""
    run_gasd_validator(fixture("rt_sem_crash_002_labeled_type_visitors.gasd"))


# ===================================================================
# RT-SEM-CRASH-003: Field alias parsing (AS on TYPE fields)
# ===================================================================

def test_rt_sem_crash_003_field_alias():
    """TYPE fields with @annotation AS ALIAS must parse and validate without errors."""
    run_gasd_validator(fixture("rt_sem_crash_003_field_alias.gasd"))


# ===================================================================
# RT-SEM-CRASH-004: LINT-001 for ACHIEVE inside ON_ERROR
# ===================================================================

def test_rt_sem_crash_004_onerror_achieve():
    """ACHIEVE inside ON_ERROR with POSTCONDITION must pass validation."""
    run_gasd_validator(fixture("rt_sem_crash_004_onerror_achieve.gasd"))


# ===================================================================
# RT-SEM-CRASH-005: CONSTRAINT inline string parsing
# ===================================================================

def test_rt_sem_crash_005_constraint_inline():
    """CONSTRAINT with inline string and annotation must parse without errors."""
    run_gasd_validator(fixture("rt_sem_crash_005_constraint_inline.gasd"))


# ===================================================================
# RT-SEM-CRASH-006: Missing custom type detection
# ===================================================================

def test_rt_sem_crash_006_custom_type_resolution():
    """Declared custom types must resolve without UnknownType errors."""
    run_gasd_validator(fixture("rt_sem_crash_006_custom_type_resolution.gasd"))


# ===================================================================
# RT-SEM-CRASH-007: Assumption annotation placement
# ===================================================================

def test_rt_sem_crash_007_assumption_annotation():
    """ASSUMPTION with @annotation AS ALIAS on header line must parse correctly."""
    run_gasd_validator(fixture("rt_sem_crash_007_assumption_annotation.gasd"))


# ===================================================================
# RT-SEM-CRASH-008: Contract structure validation
# ===================================================================

def test_rt_sem_crash_008_contract_structure():
    """CONTRACT block with BEHAVIORS/CASE/POSTCONDITION/THROWS must validate."""
    run_gasd_validator(fixture("rt_sem_crash_008_contract_structure.gasd"))


# ===================================================================
# RT-SEM-CRASH-011: Inline field_def inside type_def
# ===================================================================

def test_rt_sem_crash_011_inline_field_def():
    """Inline TYPE definitions (TYPE Point: x: Integer) must parse without TypeError."""
    run_gasd_validator(fixture("rt_sem_crash_011_inline_field_def.gasd"))


# ===================================================================
# RT-SEM-CRASH-012: Full suite cross-file validation
# All regression fixtures validated together (cross-AST type resolution)
# ===================================================================

def test_rt_sem_crash_012_full_suite():
    """All regression fixtures must pass when validated together (cross-file resolution)."""
    fixtures = [
        fixture("rt_sem_crash_001_signatures_null_safety.gasd"),
        fixture("rt_sem_crash_002_labeled_type_visitors.gasd"),
        fixture("rt_sem_crash_003_field_alias.gasd"),
        fixture("rt_sem_crash_004_onerror_achieve.gasd"),
        fixture("rt_sem_crash_005_constraint_inline.gasd"),
        fixture("rt_sem_crash_006_custom_type_resolution.gasd"),
        fixture("rt_sem_crash_008_contract_structure.gasd"),
        fixture("issue_semantic_crash.gasd"),
        fixture("rt_sem_crash_011_inline_field_def.gasd"),
    ]
    run_gasd_validator(*fixtures)


# ===================================================================
# RT-SEM-CRASH-013: Existing example suite still passes
# ===================================================================

def test_rt_sem_crash_013_full_example_suite():
    """All GASD 1.2 examples must pass validation (regression guard)."""
    example_dir = os.path.join(PROJECT_ROOT, "Specs", "examples", "gasd-1.2")
    gasd_files = sorted([
        os.path.join(example_dir, f) for f in os.listdir(example_dir) if f.endswith(".gasd")
    ])
    assert len(gasd_files) > 0, "No GASD 1.2 example files found"
    run_gasd_validator(*gasd_files)
