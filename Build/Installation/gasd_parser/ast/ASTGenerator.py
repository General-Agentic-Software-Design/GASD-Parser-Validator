from .ASTNodes import *
from ..parser.generated.grammar.GASDParser import GASDParser
from ..parser.generated.grammar.GASDParserVisitor import GASDParserVisitor

class ASTGenerator(GASDParserVisitor):
    def __init__(self, source_file="unknown"):
        self.source_file = source_file

    def _get_loc(self, ctx):
        return {
            "line": ctx.start.line,
            "column": ctx.start.column,
            "sourceFile": self.source_file
        }

    def visitGasd_file(self, ctx: GASDParser.Gasd_fileContext):
        directives = []
        decisions = []
        types = []
        components = []
        flows = []
        strategies = []
        constraints = []
        questions = []
        approvals = []
        todos = []
        reviews = []
        ensures = []
        matches = []

        for section in ctx.section():
            node = self.visit(section)
            if isinstance(node, Directive): directives.append(node)
            elif isinstance(node, Decision): decisions.append(node)
            elif isinstance(node, TypeDefinition): types.append(node)
            elif isinstance(node, ComponentDefinition): components.append(node)
            elif isinstance(node, FlowDefinition): flows.append(node)
            elif isinstance(node, StrategyDefinition): strategies.append(node)
            elif isinstance(node, ConstraintNode): constraints.append(node)
            elif isinstance(node, QuestionNode): questions.append(node)
            elif isinstance(node, ApprovalNode): approvals.append(node)
            elif isinstance(node, TodoNode): todos.append(node)
            elif isinstance(node, ReviewNode): reviews.append(node)
            elif isinstance(node, EnsureNode): ensures.append(node)
            elif isinstance(node, MatchNode): matches.append(node)

        loc = self._get_loc(ctx)
        return GASDFile(
            directives=directives,
            decisions=decisions,
            types=types,
            components=components,
            flows=flows,
            strategies=strategies,
            constraints=constraints,
            questions=questions,
            approvals=approvals,
            todos=todos,
            reviews=reviews,
            ensures=ensures,
            matches=matches,
            **loc
        )

    def visitEnsure_stmt(self, ctx: GASDParser.Ensure_stmtContext):
        return EnsureNode(expression=ctx.STRING_LITERAL().getText().strip('"'), **self._get_loc(ctx))

    def visitMatch_section(self, ctx: GASDParser.Match_sectionContext):
        return self.visit(ctx.match_expr())

    def visitContext_dir(self, ctx: GASDParser.Context_dirContext):
        return Directive(directiveType="CONTEXT", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitValue(self, ctx: GASDParser.ValueContext):
        return ctx.getText()
    def visitTarget_dir(self, ctx: GASDParser.Target_dirContext):
        return Directive(directiveType="TARGET", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitTrace_dir(self, ctx: GASDParser.Trace_dirContext):
        return Directive(directiveType="TRACE", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitNamespace_stmt(self, ctx: GASDParser.Namespace_stmtContext):
        val = ctx.STRING_LITERAL().getText().strip('"') if ctx.STRING_LITERAL() else "unknown"
        return Directive(directiveType="NAMESPACE", values=[val], **self._get_loc(ctx))

    def visitImport_stmt(self, ctx: GASDParser.Import_stmtContext):
        val = ctx.STRING_LITERAL().getText().strip('"') if ctx.STRING_LITERAL() else "unknown"
        alias = ctx.soft_id().getText() if ctx.soft_id() else None
        return Directive(directiveType="IMPORT", values=[val], alias=alias, **self._get_loc(ctx))

    def visitDecision_blk(self, ctx: GASDParser.Decision_blkContext):
        loc = self._get_loc(ctx)
        sl = ctx.STRING_LITERAL()
        name = sl[0].getText().strip('"') if len(sl) > 0 else "Unknown"
        chosen = sl[1].getText().strip('"') if len(sl) > 1 else ""
        
        # Handle RATIONALE correctly based on RATIONALE_KW presence
        rationale = None
        if ctx.RATIONALE_KW():
            # If RATIONALE_KW exists, it must be the 3rd STRING_LITERAL (index 2)
            # because the 1st is name and 2nd is chosen.
            rationale = sl[2].getText().strip('"') if len(sl) > 2 else None
        
        alternatives = []
        if ctx.ALTERNATIVES_KW():
            # Find the list literal following ALTERNATIVES
            idx = -1
            for i in range(ctx.getChildCount()):
                if ctx.getChild(i).getText() == "ALTERNATIVES":
                    # Check if next child or next-next is list_literal
                    for j in range(i+1, min(i+4, ctx.getChildCount())):
                        child = ctx.getChild(j)
                        if isinstance(child, GASDParser.List_literalContext):
                            idx = j
                            break
                    if idx != -1: break
            if idx != -1:
                alt_node = ctx.getChild(idx)
                alternatives = [v.getText().strip('"') for v in alt_node.value()]
                if "*" in alt_node.getText():
                    alternatives.append("*")

        affects = []
        if ctx.AFFECTS_KW():
            # Find the list literal following AFFECTS
            idx = -1
            for i in range(ctx.getChildCount()):
                if ctx.getChild(i).getText() == "AFFECTS":
                    for j in range(i+1, min(i+4, ctx.getChildCount())):
                        child = ctx.getChild(j)
                        if isinstance(child, GASDParser.List_literalContext):
                            idx = j
                            break
                    if idx != -1: break
            if idx != -1:
                affects_node = ctx.getChild(idx)
                affects = [v.getText().strip('"') for v in affects_node.value()]
                if "*" in affects_node.getText():
                    affects.append("*")

        return Decision(name=name, chosen=chosen, rationale=rationale, alternatives=alternatives, affects=affects, **loc)

    def visitType_def(self, ctx: GASDParser.Type_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText() if ctx.soft_id() else "Anonymous"
        fields = []
        if ctx.field_def():
            for f in ctx.field_def():
                fields.append(self.visit(f))
        return TypeDefinition(name=name, fields=fields, **loc)

    def visitField_def(self, ctx: GASDParser.Field_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText() if ctx.soft_id() else "Anonymous"
        type_expr = self.visit(ctx.type_expr()) if ctx.type_expr() else TypeExpression(baseType="Unknown", **loc)
        return FieldNode(name=name, typeExpr=type_expr, **loc)

    # Labeled expression visitors are defined later in the class

    def visitType_expr(self, ctx: GASDParser.Type_exprContext):
        loc = self._get_loc(ctx)
        
        # 1. Special case: ENUM_KW LPAREN (soft_id | STRING_LITERAL) (COMMA (soft_id | STRING_LITERAL))* RPAREN
        if ctx.ENUM_KW():
            # Collect all identifiers and string literals from the enum list
            values = []
            for i in range(ctx.getChildCount()):
                child = ctx.getChild(i)
                # Check for either soft_id (identifier) or STRING_LITERAL
                if isinstance(child, GASDParser.Soft_idContext):
                    values.append(child.getText())
                elif hasattr(child, 'getSymbol') and child.getSymbol().type == GASDParser.STRING_LITERAL:
                    values.append(child.getText())
                elif hasattr(child, 'getText') and child.getText().startswith('"'):
                    # Fallback for string literals if getSymbol() is not available or mismatch
                    values.append(child.getText())
            
            return TypeExpression(baseType="Enum", enumValues=values, **loc)
            
        # 2. Special case: OPTIONAL_KW LANGLE type_expr RANGLE
        if ctx.OPTIONAL_KW():
            args = [self.visit(a) for a in ctx.type_expr() if a]
            if args:
                # Wrap the inner type as optional, preserving all its attributes
                inner = args[0]
                return TypeExpression(
                    baseType=inner.baseType, 
                    genericArgs=inner.genericArgs, 
                    isOptional=True, 
                    literalValue=inner.literalValue,
                    enumValues=inner.enumValues,
                    **loc
                )
            return TypeExpression(baseType="Any", isOptional=True, **loc)

        # 3. Unified Generics branch: (soft_id | STRING_LITERAL) (DOT soft_id)* (LANGLE type_expr (COMMA type_expr)* RANGLE)?
        if ctx.soft_id() or (ctx.STRING_LITERAL() and ctx.LANGLE()):
            segments = [id.getText() for id in ctx.soft_id() if id]
            base = ".".join(segments)
            args = [self.visit(a) for a in ctx.type_expr() if a]
            
            is_optional = base == "Optional"
            if is_optional and args:
                inner = args[0]
                return TypeExpression(
                    baseType=inner.baseType, 
                    genericArgs=inner.genericArgs, 
                    isOptional=True, 
                    literalValue=inner.literalValue,
                    enumValues=inner.enumValues,
                    **loc
                )
            
            # For List and Map, we should also propagate something if relevant, 
            # but usually they are containers for other types.
            return TypeExpression(baseType=base, genericArgs=args, isOptional=is_optional, **loc)

        # 4. Literal types
        if ctx.STRING_LITERAL():
            literal_value = ctx.STRING_LITERAL(0).getText()
            return TypeExpression(baseType="literal", literalValue=literal_value, **loc)
        elif ctx.INTEGER():
            literal_value = str(ctx.INTEGER().getText())
            return TypeExpression(baseType="literal", literalValue=literal_value, **loc)
        elif ctx.FLOAT_LITERAL():
            literal_value = str(ctx.FLOAT_LITERAL().getText())
            return TypeExpression(baseType="literal", literalValue=literal_value, **loc)

        return TypeExpression(baseType="unknown", **loc)

    def visitComponent_def(self, ctx: GASDParser.Component_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        
        # Use a temporary holder for the component data
        self._current_component = {
            "pattern": None,
            "dependencies": [],
            "methods": [],
            "fields": []
        }
        
        for item in ctx.component_body_item():
            self.visit(item)
            
        res = ComponentDefinition(
            name=name, 
            pattern=self._current_component["pattern"],
            methods=self._current_component["methods"],
            dependencies=self._current_component["dependencies"],
            **loc
        )
        del self._current_component
        return res

    def visitComponent_body_item(self, ctx: GASDParser.Component_body_itemContext):
        if ctx.PATTERN_KW():
            val = ctx.getChild(2).getText().strip('"')
            self._current_component["pattern"] = val
        elif ctx.DEPENDENCIES_KW():
            list_node = ctx.list_literal()
            self._current_component["dependencies"] = [v.getText().strip('"') for v in list_node.value()]
            if "*" in list_node.getText():
                self._current_component["dependencies"].append("*")
        elif ctx.INTERFACE_KW():
            for m in ctx.method_sig():
                self._current_component["methods"].append(self.visit(m))
            for f in ctx.field_def():
                # We could add fields to ComponentDefinition if needed, but for now just skip or log
                pass
        return None
    def visitMethod_sig(self, ctx: GASDParser.Method_sigContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        params = self.visit(ctx.param_list()) if ctx.param_list() else []
        ret = self.visit(ctx.type_expr()) if ctx.type_expr() else None
        return MethodSignature(name=name, parameters=params, returnType=ret, **loc)

    def visitParam_list(self, ctx: GASDParser.Param_listContext):
        return [self.visit(p) for p in ctx.param()]

    def visitParam(self, ctx: GASDParser.ParamContext):
        name = ctx.soft_id().getText()
        t = self.visit(ctx.type_expr()) if ctx.type_expr() else TypeExpression(baseType="Any")
        return Parameter(name=name, type=t)

    def visitFlow_def(self, ctx: GASDParser.Flow_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        params = self.visit(ctx.param_list()) if ctx.param_list() else []
        ret = self.visit(ctx.type_expr()) if ctx.type_expr() else None
        
        steps = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.Field_defContext, GASDParser.Match_exprContext)):
                res = self.visit(child)
                if isinstance(res, list):
                    steps.extend(res)
                elif res:
                    steps.append(res)
                    
        return FlowDefinition(name=name, parameters=params, steps=steps, returnType=ret, **loc)

    def visitFlow_step(self, ctx: GASDParser.Flow_stepContext):
        loc = self._get_loc(ctx)
        
        # Case 1: annotations NEWLINE (standalone annotation)
        if ctx.annotations() and not ctx.STEP_NUM():
            substeps = []
            if ctx.internal_block():
                substeps.extend(self.visit(ctx.internal_block()))
            return FlowStepNode(
                action="ANNOTATION", 
                target="", 
                annotations=self.visit(ctx.annotations()), 
                subSteps=substeps,
                **loc
            )

        num = int(ctx.STEP_NUM().getText().rstrip(".")) if ctx.STEP_NUM() else None
        
        step_annotations = self.visit(ctx.annotations()) if ctx.annotations() else []
        
        action_name = "ACTION"
        target = ""
        substeps = []

        as_binding = None
        type_path = None

        if ctx.action():
            action_data = self.visit(ctx.action())
            action_name = action_data["action"]
            target = action_data["target"]
            as_binding = action_data.get("as_binding")
            type_path = action_data.get("type_path")
        elif ctx.control_flow():
            cf_data = self.visit(ctx.control_flow())
            action_name = cf_data["action"]
            target = cf_data["target"]
            if "subSteps" in cf_data:
                substeps.extend(cf_data["subSteps"])
        elif ctx.match_expr():
            match_node = self.visit(ctx.match_expr())
            action_name = "MATCH"
            target = match_node.expression
            substeps.append(match_node)

        # Visit internal block if present
        if ctx.internal_block():
            substeps.extend(self.visit(ctx.internal_block()))

        return FlowStepNode(stepNumber=num, action=action_name, target=target, asBinding=as_binding, typePath=type_path, subSteps=substeps, annotations=step_annotations, **loc)

    def visitInternal_block(self, ctx: GASDParser.Internal_blockContext):
        substeps = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.Step_propertyContext, GASDParser.Otherwise_stmtContext)):
                substeps.append(self.visit(child))
        return substeps

    def visitMatch_expr(self, ctx: GASDParser.Match_exprContext):
        loc = self._get_loc(ctx)
        if ctx.expr():
            expr_text = ctx.expr().getText()
        else:
            expr_text = " ".join([id.getText() for id in ctx.soft_id()])
        cases = [self.visit(c) for c in ctx.match_case()]
        return MatchNode(expression=expr_text, cases=cases, **loc)

    def visitMatch_case(self, ctx: GASDParser.Match_caseContext):
        cond = ctx.getChild(0).getText()
        # Find the result part (index 2 or the block)
        res_node = ctx.getChild(2)
        if isinstance(res_node, GASDParser.Match_case_block_itemsContext):
            target = str(self.visit(res_node))
        else:
            target = res_node.getText()
        return MatchCase(condition=cond, target=target)

    def visitMatch_case_block_items(self, ctx: GASDParser.Match_case_block_itemsContext):
        substeps = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.Match_exprContext)):
                res = self.visit(child)
                if res: substeps.append(res)
        return substeps

    def _get_text(self, node_or_list, index=0):
        if node_or_list is None: return ""
        if isinstance(node_or_list, list):
            return node_or_list[index].getText() if len(node_or_list) > index else ""
        return node_or_list.getText()

    def visitParenExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitNotExpr(self, ctx):
        return f"NOT {self.visit(ctx.expr())}"

    def visitArithmeticExpr(self, ctx):
        op = ctx.op.text
        return f"{self.visit(ctx.left)} {op} {self.visit(ctx.right)}"

    def visitComparisonExpr(self, ctx):
        if ctx.comparison_op():
            op = ctx.comparison_op().getText()
        else:
            op = "HAS"
        return f"{self.visit(ctx.left)} {op} {self.visit(ctx.right)}"

    def visitLogicalExpr(self, ctx):
        op = "AND" if ctx.AND_KW() else "OR"
        return f"{self.visit(ctx.left)} {op} {self.visit(ctx.right)}"

    def visitValueExpr(self, ctx):
        return self.visit(ctx.value())

    def visitAction(self, ctx: GASDParser.ActionContext):
        # Universal action visitor
        # action : VALIDATE_KW ... | ACHIEVE_KW ... | CREATE_KW ... | PERSIST_KW ... | ...
        action_name = ctx.getChild(0).getText()
        target = ""
        
        if ctx.VALIDATE_KW():
            target = ctx.expr(0).getText() if ctx.expr(0) else ""
            as_binding = "AS TYPE"
            type_path = ctx.type_expr().getText() if ctx.type_expr() else ""
            return {"action": "VALIDATE", "target": target, "as_binding": as_binding, "type_path": type_path}
        elif ctx.ACHIEVE_KW():
            sl = ctx.STRING_LITERAL()
            if isinstance(sl, list):
                titles = " AND ".join([s.getText() for s in sl])
            else:
                titles = sl.getText() if sl else ""
            expr_val = ""
            if ctx.expr():
                expr_val = f": {self._get_text(ctx.expr(), 0)}"
            target = f"{titles}{expr_val}"
        elif ctx.CREATE_KW() or ctx.RETURN_KW() or ctx.LOG_KW() or ctx.THROW_KW() or ctx.EXECUTE_KW() or ctx.UPDATE_KW():
            # For these, the target is the rest of the line content
            target = ctx.getText()[len(action_name):].strip()
        elif ctx.PERSIST_KW():
            target = self._get_text(ctx.expr(), 0)
            if ctx.VIA_KW(): target += f" via {self._get_text(ctx.expr(), 1)}"
        elif ctx.TRANSFORM_KW():
            if ctx.expr():
                target = self._get_text(ctx.expr(), 0)
                if len(ctx.expr()) > 1: target += f" via {self._get_text(ctx.expr(), 1)}"
            elif ctx.annotation():
                target = f"({ctx.annotation().getText()})"
        elif hasattr(ctx, 'soft_id') and ctx.soft_id():
            # generic action or function call
            target = ctx.getText()
            if target.startswith(action_name):
                target = target[len(action_name):].strip()
        
        return {"action": action_name, "target": target}

    def visitControl_flow(self, ctx: GASDParser.Control_flowContext):
        loc = self._get_loc(ctx)
        if ctx.ENSURE_KW():
            parts = []
            for i in range(1, ctx.getChildCount()):
                child = ctx.getChild(i)
                if not isinstance(child, GASDParser.AnnotationsContext):
                    parts.append(child.getText())
            target = " ".join(parts).strip()
            return {"action": "ENSURE", "target": target}
            
        if ctx.IF_KW() or ctx.ON_ERROR_KW():
            action_name = "IF" if ctx.IF_KW() else "ON_ERROR"
            target = self._get_text(ctx.expr(), 0) if ctx.expr() else ""
            substeps = []
            for i in range(ctx.getChildCount()):
                child = ctx.getChild(i)
                if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.ActionContext)):
                    res = self.visit(child)
                    if res:
                        if isinstance(res, dict):
                            substeps.append(FlowStepNode(action=res["action"], target=res["target"], **loc))
                        else:
                            substeps.append(res)
            return {"action": action_name, "target": target, "subSteps": substeps}

        action_name = ctx.getChild(0).getText()
        target = self._get_text(ctx.expr())
        return {"action": action_name, "target": target}

    def visitOtherwise_stmt(self, ctx: GASDParser.Otherwise_stmtContext):
        loc = self._get_loc(ctx)
        action_type = "THROW" if ctx.THROW_KW() else "RETURN"
        target = ctx.expr().getText()
        return FlowStepNode(stepNumber=None, action="OTHERWISE", target=f"{action_type} {target}", **loc)

    def visitStep_property(self, ctx: GASDParser.Step_propertyContext):
        name = ctx.soft_id().getText()
        val = ""
        if ctx.expr():
            val = self.visit(ctx.expr())
        elif ctx.value_list():
            val = ctx.value_list().getText()
            
        loc = self._get_loc(ctx)
        # Map step property to a FlowStepNode with action="PROPERTY" to fit in subSteps
        return FlowStepNode(stepNumber=None, action="PROPERTY", target=f"{name}: {val}", **loc)

    def visitAnnotations(self, ctx: GASDParser.AnnotationsContext):
        return [self.visit(a) for a in ctx.annotation()]

    def visitConstraint_stmt(self, ctx: GASDParser.Constraint_stmtContext):
        name = ctx.soft_id().getText() if ctx.soft_id() else None
        if ctx.STRING_LITERAL():
            text = ctx.STRING_LITERAL().getText().strip('"')
        elif ctx.value():
            text = ctx.value().getText().strip('"')
        else:
            # Fallback to children or full text if specifically formatted
            text = ctx.getText().strip()
            if ":" in text and name:
                text = text.split(":", 1)[1].strip()
        return ConstraintNode(kind="Constraint", text=text, name=name, **self._get_loc(ctx))

    def visitInvariant_stmt(self, ctx: GASDParser.Invariant_stmtContext):
        name = ctx.soft_id().getText() if ctx.soft_id() else None
        if ctx.STRING_LITERAL():
            text = ctx.STRING_LITERAL().getText().strip('"')
        elif ctx.value():
            text = ctx.value().getText().strip('"')
        else:
            text = ctx.getText().strip()
            if ":" in text and name:
                text = text.split(":", 1)[1].strip()
        return ConstraintNode(kind="Invariant", text=text, name=name, **self._get_loc(ctx))

    def visitTodo_stmt(self, ctx: GASDParser.Todo_stmtContext):
        return TodoNode(text=ctx.STRING_LITERAL().getText().strip('"'), **self._get_loc(ctx))

    def visitReview_stmt(self, ctx: GASDParser.Review_stmtContext):
        return ReviewNode(text=ctx.STRING_LITERAL().getText().strip('"'), **self._get_loc(ctx))

    def visitQuestion_stmt(self, ctx: GASDParser.Question_stmtContext):
        return QuestionNode(text=ctx.STRING_LITERAL().getText().strip('"'), **self._get_loc(ctx))

    def visitApprove_blk(self, ctx: GASDParser.Approve_blkContext):
        loc = self._get_loc(ctx)
        target = ctx.STRING_LITERAL(0).getText().strip('"')
        status = "APPROVED" # Simplified
        by = ctx.STRING_LITERAL(1).getText().strip('"')
        date = ctx.STRING_LITERAL(2).getText().strip('"')
        return ApprovalNode(target=target, status=status, by=by, date=date, **loc)

    def visitStrategy_def(self, ctx: GASDParser.Strategy_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        algo = ""
        comp = ""
        prec = None
        inputs = []
        output = TypeExpression(baseType="Any")

        for item in ctx.strategy_item():
            child_text = item.getChild(0).getText()
            if child_text == "ALGORITHM":
                algo = item.STRING_LITERAL(0).getText().strip('"') if item.STRING_LITERAL() else ""
            elif child_text == "COMPLEXITY":
                comp = item.expr().getText() if item.expr() else ""
            elif child_text == "PRECONDITION":
                prec = item.expr().getText() if item.expr() else ""
            elif child_text == "INPUT":
                if item.param_list():
                    inputs = self.visit(item.param_list())
                else:
                    inputs = [self.visit(p) for p in item.param()]
            elif child_text == "OUTPUT":
                output = self.visit(item.type_expr())

        return StrategyDefinition(name=name, algorithm=algo, precondition=prec, complexity=comp, inputs=inputs, output=output, **loc)

