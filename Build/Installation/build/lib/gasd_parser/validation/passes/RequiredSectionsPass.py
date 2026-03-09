from typing import List
from ..ValidationPipeline import ValidationPass, SemanticError
from ...ast.ASTNodes import GASDFile

class RequiredSectionsPass(ValidationPass):
    """
    Pass 2: Required Sections Validation
    Ensures mandatory directives and structure are present.
    @trace #AC-PARSER-004-02
    """
    name = "RequiredSectionsPass"

    def validate(self, ast: GASDFile) -> List[SemanticError]:
        errors = []
        
        has_context = False
        has_target = False
        
        for d in ast.directives:
            if d.directiveType == "CONTEXT":
                has_context = True
            if d.directiveType == "TARGET":
                has_target = True

        if not has_context:
            errors.append(SemanticError(
                code='V002',
                severity='ERROR',
                message="Missing required CONTEXT directive.",
                line=1, column=1
            ))
            
        if not has_target:
            errors.append(SemanticError(
                code='V003',
                severity='ERROR',
                message="Missing required TARGET directive.",
                line=1, column=1
            ))
            
        if not (ast.types or ast.components or ast.flows):
            errors.append(SemanticError(
                code='V004',
                severity='ERROR',
                message="File must contain at least one TYPE, COMPONENT, or FLOW.",
                line=1, column=1
            ))
            
        for comp in ast.components:
            if not comp.methods:  # AC-PARSER-004-02: Component must have interface
                errors.append(SemanticError(
                    code='V005',
                    severity='ERROR',
                    message=f"COMPONENT '{comp.name}' must have an INTERFACE block with at least one method.",
                    line=comp.line, column=comp.column,
                    context=comp.name
                ))
                
        for dec in ast.decisions:
            if not dec.chosen:
                errors.append(SemanticError(
                    code='V006',
                    severity='ERROR',
                    message=f"DECISION '{dec.name}' must have a CHOSEN field.",
                    line=dec.line, column=dec.column,
                    context=dec.name
                ))
            if not dec.alternatives:
                errors.append(SemanticError(
                    code='V014',
                    severity='ERROR',
                    message=f"DECISION '{dec.name}' must have at least one ALTERNATIVE.",
                    line=dec.line, column=dec.column,
                    context=dec.name
                ))
                
        for s in ast.strategies:
            if not s.algorithm:
                errors.append(SemanticError(
                    code='V013',
                    severity='ERROR',
                    message=f"STRATEGY '{s.name}' must define an ALGORITHM.",
                    line=s.line, column=s.column,
                    context=s.name
                ))
                
        for f in ast.flows:
            if not f.steps:
                errors.append(SemanticError(
                    code='V007',
                    severity='ERROR',
                    message=f"FLOW '{f.name}' must have at least one step.",
                    line=f.line, column=f.column,
                    context=f.name
                ))

        return errors
