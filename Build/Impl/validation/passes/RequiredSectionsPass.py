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
        has_namespace = False
        
        is_v12 = getattr(ast, 'version', '1.1') == "1.2"
        
        for d in ast.directives:
            if d.directiveType == "CONTEXT":
                has_context = True
            if d.directiveType == "TARGET":
                has_target = True
            if d.directiveType == "NAMESPACE":
                has_namespace = True

        # NAMESPACE serves as the modern equivalent of CONTEXT
        if not has_context and not has_namespace and not is_v12:
            errors.append(SemanticError(
                code='V002',
                severity='ERROR',
                message="Missing required CONTEXT directive.",
                line=1, column=1
            ))
            
        if not has_target and not is_v12:
            errors.append(SemanticError(
                code='V003',
                severity='ERROR',
                message="Missing required TARGET directive.",
                line=1, column=1
            ))
            
        # GEP-6: GASD 1.2 permits header-only files and IMPORT-only files
        has_imports = any(d.directiveType == "IMPORT" for d in ast.directives)
        has_assumptions = getattr(ast, 'assumptions', None) and len(ast.assumptions) > 0
        has_invariants = getattr(ast, 'ensures', None) and len(ast.ensures) > 0
        if not is_v12 and not (ast.types or ast.components or ast.flows or ast.contracts or ast.models or ast.constraints or ast.decisions or has_imports or has_assumptions):
            errors.append(SemanticError(
                code='V004',
                severity='ERROR',
                message="File must contain at least one TYPE, COMPONENT, FLOW, CONTRACT, MODEL, DECISION, INVARIANT or IMPORT.",
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
