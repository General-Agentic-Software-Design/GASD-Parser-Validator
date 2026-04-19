# Bug Report: `RATIONALE` field in `DECISION` blocks is incorrectly optional

## Description

The GASD parser currently treats the `RATIONALE` field inside a `DECISION` block as an optional field. However, according to the official, authoritative GASD 1.2.0 Specification (`GASD_Specification.md`), `RATIONALE` is formally defined as a MUST (mandatory) requirement for all Architectural Decisions.

Because the parser allows files to omit the rationale without throwing an error, users can generate GASD designs that lack proper architectural reasoning while still passing syntax validation, leading to non-compliant GASD usage.

## Root Cause

There is a discrepancy between the authoritative specification document and the parser implementation:

1. **Parser Grammar (`Impl/grammar/GASDParser.g4`)**: The `decision_blk` rule incorrectly adds an optional modifier `?` to the rationale line:
   ```antlr
   (RATIONALE_KW COLON STRING_LITERAL NEWLINE)?
   ```
2. **AST Node Definition (`Impl/ast/ASTNodes.py`)**: The `Decision` class defines `rationale` as an optional string.
   ```python
   rationale: Optional[str] = None
   ```

Meanwhile, the formal syntax in `GASD_Specification.md` defines it without the optional brackets:
```gasd
DECISION "[Decision Name]" [Annotations]:
    CHOSEN: "[Choice]"
    RATIONALE: "[Reasoning]"
    [ALTERNATIVES: ["[Alt1]", "[Alt2]"]]
    ...
```

## Proposed Fix

1. **Update `GASDParser.g4`**: Remove the `?` token from the `RATIONALE` rule so that a syntax error is raised if `RATIONALE` is omitted.
   ```antlr
   decision_blk
       : DECISION_KW STRING_LITERAL annotations? COLON NEWLINE
         INDENT
         CHOSEN_KW COLON STRING_LITERAL NEWLINE
         RATIONALE_KW COLON STRING_LITERAL NEWLINE
         (ALTERNATIVES_KW COLON list_literal NEWLINE)?
         (AFFECTS_KW COLON list_literal NEWLINE)?
         DEDENT
       ;
   ```

2. **Update `ASTNodes.py`**: Change the `Decision` dataclass so that `rationale` is a strictly typed string rather than `Optional`.
   ```python
   @dataclass
   class Decision(ASTNodeBase):
       name: str = ""
       chosen: str = ""
       rationale: str = ""
       kind: str = "Decision"
       alternatives: Optional[List[str]] = None
       affects: Optional[List[str]] = None
   ```

3. Re-compile the ANTLR grammar so that the python implementations (`gasd_parser/parser/generated/...`) are appropriately updated to reflect the new rule constraint.

4. **Add Regression & Acceptance Tests**:
   - Create a positive acceptance test verifying that a `DECISION` block with a `RATIONALE` compiles correctly and correctly structures the AST.
   - Create a negative regression test ensuring that a `DECISION` block missing a `RATIONALE` throws a hard syntax validation error in the parser and fails the test suite. This guarantees the permissiveness regression will not happen again in future releases.

## Impact

Applying this fix will ensure the parser throws a hard syntax error if an author fails to include a `RATIONALE` block in their `DECISION`, aggressively enforcing documentation of architectural reasoning exactly as mandated by the GASD 1.2.0 Specification.
