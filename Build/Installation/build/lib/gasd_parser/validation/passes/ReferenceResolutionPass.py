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
        
        # Determine file version (GEP-6)
        file_version = getattr(ast, "version", None) or "1.2"
        warning_level = 'INFO' if file_version == "1.1" else 'WARNING'

        # Build symbol table
        declared_components = {c.name for c in ast.components}
        declared_types = {t.name for t in ast.types}
        declared_constructs = set()
        declared_constructs.update(declared_components)
        declared_constructs.update(declared_types)
        declared_constructs.update({f.name for f in ast.flows})
        declared_constructs.update({s.name for s in ast.strategies})
        declared_constructs.update({d.name for d in ast.decisions})
        
        primitive_types = {"String", "Integer", "Int", "Float", "Decimal", "Boolean", "Bytes", "UUID", "DateTime", "List", "Map", "Optional", "Result", "Any", "Void", "Enum"}
        
        from ...semantic.SymbolTable import BuiltinTypeRegistry

        def check_type_expr(expr, location_node, context_name):
            if not expr: return
            # GASD 1.1: Literal types (baseType == "literal") are self-resolving; skip resolution.
            if expr.literalValue is not None:
                return
                
            # Built-in Generic Argument Validation @trace #AC-SEMAST-019-03
            # GASD: Primitives can be shadowed by local types (e.g. TYPE Result in examples)
            if expr.baseType in primitive_types and expr.baseType not in declared_types:
                arg_count = len(expr.genericArgs or [])
                err_msg = BuiltinTypeRegistry.validateGenerics(expr.baseType, arg_count)
                if err_msg:
                    errors.append(SemanticError(
                        code='V008',
                        severity='ERROR',
                        message=err_msg,
                        line=location_node.line, column=location_node.column,
                        context=context_name
                    ))

            if expr.baseType and expr.baseType not in primitive_types and expr.baseType not in declared_types and "." not in expr.baseType:
                errors.append(SemanticError(
                    code='V008',
                    severity=warning_level,
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
                            severity=warning_level,
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
                    if affect != "*" and affect not in declared_constructs:
                        errors.append(SemanticError(
                            code='V010',
                            severity=warning_level,
                            message=f"DECISION '{dec.name}' affects unknown construct '{affect}'",
                            line=dec.line, column=dec.column,
                            context=dec.name
                        ))

        # Validate Flow types and VALIDATE bindings
        def check_steps(steps, context_name):
            if not steps: return
            for step in steps:
                # 1. Safely check for action type
                if hasattr(step, "action") and step.action == "VALIDATE":
                    if not step.asBinding or not step.typePath:
                        errors.append(SemanticError(
                            code='V012',
                            severity='ERROR',
                            message=f"VALIDATE action requires explicit 'AS TYPE.X' binding",
                            line=step.line, column=step.column,
                            context=context_name
                        ))
                    elif step.typePath not in declared_types and step.typePath not in primitive_types:
                         errors.append(SemanticError(
                            code='V011',
                            severity='ERROR',
                            message=f"VALIDATE binding resolves to unknown TYPE '{step.typePath}'",
                            line=step.line, column=step.column,
                            context=context_name
                        ))
                
                # 2. Recursively check all possible sub-step locations
                if hasattr(step, "subSteps") and step.subSteps:
                    check_steps(step.subSteps, context_name)
                if hasattr(step, "cases"): # MatchNode
                    for case in step.cases:
                        # Handle potential 'steps' or 'target' if it's a list
                        steps_to_check = getattr(case, "steps", None)
                        if not steps_to_check:
                            target = getattr(case, "target", None)
                            if isinstance(target, list):
                                steps_to_check = target
                        
                        if steps_to_check:
                            check_steps(steps_to_check, context_name)
                if hasattr(step, "thenSteps"): # IfNode
                    check_steps(step.thenSteps, context_name)
                if hasattr(step, "elseSteps"): # IfNode
                    check_steps(step.elseSteps, context_name)

        for f in ast.flows:
            for param in f.parameters:
                check_type_expr(param.type, f, f.name)
            check_type_expr(f.returnType, f, f.name)
            check_steps(f.steps, f.name)

        for s in ast.strategies:
            if s.inputs:
                for param in s.inputs:
                    check_type_expr(param.type, s, s.name)
            check_type_expr(s.output, s, s.name)
            
        # Validate Type definitions
        for t in ast.types:
            if t.fields:
                for field in t.fields:
                    check_type_expr(field.type, field, f"{t.name}.{field.name}")
                
        return errors
