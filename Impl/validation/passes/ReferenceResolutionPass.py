from typing import List
from ..ValidationPipeline import ValidationPass, SemanticError
from ...ast.ASTNodes import GASDFile

class ReferenceResolutionPass(ValidationPass):
    """
    Pass 3: Reference Resolution
    Ensures all cross-references between constructs resolve to valid targets.
    @trace #AC-PARSER-004-03
    """
    name = "ReferenceResolutionPass"

    def validate(self, ast: GASDFile) -> List[SemanticError]:
        errors = []
        
        # Build symbol table
        declared_components = {c.name for c in ast.components}
        declared_types = {t.name for t in ast.types}
        declared_constructs = set()
        declared_constructs.update(declared_components)
        declared_constructs.update(declared_types)
        declared_constructs.update({f.name for f in ast.flows})
        declared_constructs.update({s.name for s in ast.strategies})
        declared_constructs.update({d.name for d in ast.decisions})
        
        primitive_types = {"String", "Integer", "Boolean", "Float", "Optional", "List", "Map", "Enum"}
        
        def check_type_expr(expr, location_node, context_name):
            if not expr: return
            # GASD 1.1: Literal types (baseType == "literal") are self-resolving; skip resolution.
            if expr.literalValue is not None:
                return
            if expr.baseType and expr.baseType not in primitive_types and expr.baseType not in declared_types:
                errors.append(SemanticError(
                    code='V008',
                    severity='WARNING',
                    message=f"Unknown type reference: '{expr.baseType}'",
                    line=location_node.line, column=location_node.column,
                    context=context_name
                ))
            if expr.genericArgs:
                for arg in expr.genericArgs:
                    check_type_expr(arg, location_node, context_name)

        # Validate Component dependencies
        for comp in ast.components:
            if comp.dependencies:
                for dep in comp.dependencies:
                    if dep not in declared_components:
                        errors.append(SemanticError(
                            code='V009',
                            severity='WARNING',
                            message=f"COMPONENT '{comp.name}' references unknown DEPENDENCY '{dep}'",
                            line=comp.line, column=comp.column,
                            context=comp.name
                        ))
            
            for method in comp.methods:
                for param in method.parameters:
                    check_type_expr(param.type, method, f"{comp.name}.{method.name}")
                check_type_expr(method.returnType, method, f"{comp.name}.{method.name}")

        # Validate Decision affects
        for dec in ast.decisions:
            if dec.affects:
                for affect in dec.affects:
                    if affect not in declared_constructs:
                        errors.append(SemanticError(
                            code='V010',
                            severity='WARNING',
                            message=f"DECISION '{dec.name}' affects unknown construct '{affect}'",
                            line=dec.line, column=dec.column,
                            context=dec.name
                        ))

        # Validate Flow types
        for f in ast.flows:
            for param in f.parameters:
                check_type_expr(param.type, f, f.name)
            check_type_expr(f.returnType, f, f.name)
            
        # Validate Type definitions
        for t in ast.types:
            for field in t.fields:
                check_type_expr(field.typeExpr, field, f"{t.name}.{field.name}")
                
        return errors
