# Bug Report: `AttributeError` in `ReferenceResolutionPass`

## Description

The `gasd-parser` (v1.1.1) fails with an `AttributeError` when validating GASD files that use control flow constructs like `MATCH` or `IF` within a `FLOW`. This occurs during the `ReferenceResolutionPass`, which incorrectly assumes that every step in a flow is a simple action with an `.action` attribute.

## Traceback

```text
FAIL  ./Design/app_flows.gasd
...
  File "/Users/ming/Library/Python/3.9/lib/python/site-packages/gasd_parser/validation/passes/ReferenceResolutionPass.py", line 104, in validate
    check_steps(f.steps, f.name)
  File "/Users/ming/Library/Python/3.9/lib/python/site-packages/gasd_parser/validation/passes/ReferenceResolutionPass.py", line 98, in check_steps
    check_steps(step.subSteps, context_name)
  File "/Users/ming/Library/Python/3.9/lib/python/site-packages/gasd_parser/validation/passes/ReferenceResolutionPass.py", line 80, in check_steps
    if step.action == "VALIDATE":
AttributeError: 'MatchNode' object has no attribute 'action'
```

## Root Cause

In GASD 1.1.0, the grammar was expanded to support more complex logic, including nested `MATCH` statements. The parser's validation logic in `ReferenceResolutionPass.py` was not updated to handle these non-action nodes (e.g., `MatchNode`, `IfNode`).

### Original Code (Buggy)

```python
def check_steps(steps, context_name):
    if not steps: return
    for step in steps:
        if step.action == "VALIDATE":  # <--- CRASH: MatchNode has no .action
            # ... validation logic ...
        if step.subSteps:
            check_steps(step.subSteps, context_name)
```

## Fix Implemented

I modified the `check_steps` helper function to:

1. Use `hasattr(step, "action")` before checking for the "VALIDATE" keyword.
2. Recursively traverse sub-steps within `MatchNode` cases and `IfNode` branches (`thenSteps`, `elseSteps`).

### Fixed Code

```python
def check_steps(steps, context_name):
    if not steps: return
    for step in steps:
        # 1. Safely check for action type
        if hasattr(step, "action") and step.action == "VALIDATE":
            # ... validation logic ...
        
        # 2. Recursively check all possible sub-step locations
        if hasattr(step, "subSteps") and step.subSteps:
            check_steps(step.subSteps, context_name)
        if hasattr(step, "cases"): # MatchNode
            for case in step.cases:
                if hasattr(case, "steps") and case.steps:
                    check_steps(case.steps, context_name)
        if hasattr(step, "thenSteps"): # IfNode
            check_steps(step.thenSteps, context_name)
        if hasattr(step, "elseSteps"): # IfNode
            check_steps(step.elseSteps, context_name)
```

## Impact

This fix allows the validator to correctly process complex design flows introduced in GASD 1.1.0, ensuring that `VALIDATE` bindings deep within nested logic are still checked for mandatory type references.
