from .ASTNodes import *
from ..parser.generated.grammar.GASDParser import GASDParser
from ..parser.generated.grammar.GASDParserVisitor import GASDParserVisitor

class ASTGenerator(GASDParserVisitor):
    def __init__(self, source_file="unknown"):
        self.source_file = source_file
        self.pending_annotations = []

    def visit(self, tree):
        # type_name = type(tree).__name__
        # print(f"!!!! DEBUG: visit() for {type_name} !!!!")
        return super().visit(tree)

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
        contracts = []
        models = []
        assumptions = []
        questions = []
        approvals = []
        todos = []
        reviews = []
        ensures = []
        matches = []
        version = "1.1"

        for section in ctx.section():
            node = self.visit(section)
            if not node: continue
            
            if isinstance(node, str) and getattr(section, 'version_dir', None) and section.version_dir():
                version = node
            elif isinstance(node, Directive): directives.append(node)
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
            elif isinstance(node, ContractDefinition): contracts.append(node)
            elif isinstance(node, ModelDefinition): models.append(node)
            elif isinstance(node, AssumptionDefinition): assumptions.append(node)
            elif isinstance(node, list) and len(node) > 0:
                if isinstance(node[0], str) and node[0] == "POSTCONDITION":
                    for pc in node[1:]:
                        ensures.append(EnsureNode(expression=pc, **self._get_loc(section)))
                elif isinstance(node[0], Annotation):
                    self.pending_annotations.extend(node)

        # Set GASDFile line to 1 (file root always starts at line 1)
        res_file = GASDFile(
            version=version,
            line=1,
            column=0,
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
            contracts=contracts,
            models=models,
            assumptions=assumptions,
            sourceFile=self.source_file
        )
        res_file.annotations = self.pending_annotations
        self.pending_annotations = []
        return res_file

    def visitSection(self, ctx: GASDParser.SectionContext):
        # We need an explicit visitSection because 'section : annotations NEWLINE'
        # would otherwise return the result of NEWLINE (None) instead of the annotations.
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            # Skip terminal nodes like NEWLINE
            from antlr4.tree.Tree import TerminalNodeImpl
            if not isinstance(child, TerminalNodeImpl):
                return self.visit(child)
        return None

    def visitEnsure_stmt(self, ctx: GASDParser.Ensure_stmtContext):
        return EnsureNode(expression=ctx.STRING_LITERAL().getText().strip('"'), **self._get_loc(ctx))

    def visitMatch_section(self, ctx: GASDParser.Match_sectionContext):
        return self.visit(ctx.match_expr())

    def visitContext_dir(self, ctx: GASDParser.Context_dirContext):
        return Directive(directiveType="CONTEXT", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitVersion_dir(self, ctx: GASDParser.Version_dirContext):
        return ctx.getChild(1).getText().strip('"')

    def visitValue(self, ctx: GASDParser.ValueContext):
        return ctx.getText()
    def visitVersion_dir(self, ctx: GASDParser.Version_dirContext):
        v = ctx.version_number().getText() if ctx.version_number() else ctx.STRING_LITERAL().getText().strip('"')
        return v # visitGasd_file handles this return as a version string

    def visitContext_dir(self, ctx: GASDParser.Context_dirContext):
        return Directive(directiveType="CONTEXT", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitTarget_dir(self, ctx: GASDParser.Target_dirContext):
        return Directive(directiveType="TARGET", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitTrace_dir(self, ctx: GASDParser.Trace_dirContext):
        return Directive(directiveType="TRACE", values=[v.getText() for v in ctx.value_list().value()], **self._get_loc(ctx))

    def visitNamespace_stmt(self, ctx: GASDParser.Namespace_stmtContext):
        val = ctx.STRING_LITERAL().getText().strip('"\'') if ctx.STRING_LITERAL() else "unknown"
        return Directive(directiveType="NAMESPACE", values=[val], **self._get_loc(ctx))

    def visitImport_stmt(self, ctx: GASDParser.Import_stmtContext):
        val = ctx.STRING_LITERAL().getText().strip('"\'') if ctx.STRING_LITERAL() else "unknown"
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
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        fields = []
        # Process indented block (type_body_item)
        if hasattr(ctx, 'type_body_item') and ctx.type_body_item():
            for tbi in ctx.type_body_item():
                if tbi.field_def():
                    fields.append(self.visit(tbi.field_def()))
                elif tbi.annotations():
                    self.pending_annotations += self._visit_anns(tbi.annotations())
        
        # Process inline field (field_def)
        fd_ctx = ctx.field_def()
        if fd_ctx:
            if isinstance(fd_ctx, list):
                fields.extend([self.visit(f) for f in fd_ctx])
            else:
                fields.append(self.visit(fd_ctx))
        
        # Detect enum: ENUM_KW lives in the inline type_expr child, not in type_def itself
        is_enum = False
        if ctx.type_expr():
            te_ctx = ctx.type_expr()
            if hasattr(te_ctx, 'ENUM_KW') and te_ctx.ENUM_KW():
                is_enum = True
        return TypeDefinition(name=name, fields=fields, isEnum=is_enum, annotations=anns, **loc)

    def visitField_def(self, ctx: GASDParser.Field_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText() if ctx.soft_id() else "Anonymous"
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        type_expr = self.visit(ctx.type_expr()) if ctx.type_expr() else TypeExpression(baseType="Unknown", **loc)
        return FieldDefinition(name=name, type=type_expr, annotations=anns, **loc)

    # === Labeled Type Expression Visitors ===

    def visitGenericType(self, ctx: GASDParser.GenericTypeContext):
        loc = self._get_loc(ctx)
        segments = [id.getText() for id in ctx.soft_id() if id]
        base = ".".join(segments)
        args = [self.visit(a) for a in ctx.type_expr() if a]
        
        is_optional = base == "Optional"
        return TypeExpression(baseType=base, genericArgs=args, isOptional=is_optional, **loc)

    def visitRecordType(self, ctx: GASDParser.RecordTypeContext):
        loc = self._get_loc(ctx)
        args = []
        if hasattr(ctx, 'param_list') and ctx.param_list():
             # self.visit() on param just returns a Parameter object
             args = [self.visit(p).type for p in ctx.param_list().param()]
        return TypeExpression(baseType="Record", genericArgs=args, **loc)

    def visitEnumType(self, ctx: GASDParser.EnumTypeContext):
        loc = self._get_loc(ctx)
        values = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, GASDParser.Soft_idContext):
                values.append(child.getText())
            elif hasattr(child, 'getSymbol') and child.getSymbol().type == GASDParser.STRING_LITERAL:
                values.append(child.getText())
        return TypeExpression(baseType="Enum", enumValues=values, **loc)

    def visitOptionalType(self, ctx: GASDParser.OptionalTypeContext):
        loc = self._get_loc(ctx)
        inner = self.visit(ctx.type_expr())
        if inner:
            return TypeExpression(
                baseType=inner.baseType, 
                genericArgs=inner.genericArgs, 
                isOptional=True, 
                **loc
            )
        return TypeExpression(baseType="Any", isOptional=True, **loc)

    def visitSimpleType(self, ctx: GASDParser.SimpleTypeContext):
        loc = self._get_loc(ctx)
        segments = [id.getText() for id in ctx.soft_id() if id]
        base = ".".join(segments)
        if hasattr(ctx, 'STRING_LITERAL') and ctx.STRING_LITERAL():
            return TypeExpression(baseType="literal", literalValue=ctx.STRING_LITERAL().getText(), **loc)
        return TypeExpression(baseType=base, **loc)

    def visitIntType(self, ctx: GASDParser.IntTypeContext):
        loc = self._get_loc(ctx)
        return TypeExpression(baseType="literal", literalValue=ctx.INTEGER().getText(), **loc)

    def visitFloatType(self, ctx: GASDParser.FloatTypeContext):
        loc = self._get_loc(ctx)
        return TypeExpression(baseType="literal", literalValue=ctx.FLOAT_LITERAL().getText(), **loc)

    # Fallback for the rule itself if needed
    def visitType_expr(self, ctx: GASDParser.Type_exprContext):
        return self.visitChildren(ctx)

    def visitComponent_def(self, ctx: GASDParser.Component_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        
        v_anns = self._visit_anns(ctx.annotations()) if ctx.annotations() else []
        anns = self.pending_annotations + v_anns
        self.pending_annotations = []
        
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
            annotations=anns,
            **loc
        )
        self.pending_annotations = []
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
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        params = self.visit(ctx.param_list()) if ctx.param_list() else []
        ret = self.visit(ctx.type_expr()) if ctx.type_expr() else None
        return MethodSignature(name=name, parameters=params, returnType=ret, annotations=anns, **loc)

    def visitParam_list(self, ctx: GASDParser.Param_listContext):
        return [self.visit(p) for p in ctx.param()]

    def visitParam(self, ctx: GASDParser.ParamContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText()
        t = self.visit(ctx.type_expr()) if ctx.type_expr() else TypeExpression(baseType="Any")
        anns = self._visit_anns(ctx.annotations())
        return Parameter(name=name, type=t, annotations=anns, **loc)

    def visitFlow_def(self, ctx: GASDParser.Flow_defContext):
        loc = self._get_loc(ctx)
        name = ctx.soft_id().getText() if ctx.soft_id() else "Anonymous"
        
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        
        params = self.visit(ctx.param_list()) if ctx.param_list() else []
        ret = self.visit(ctx.type_expr()) if ctx.type_expr() else None
        
        steps = []
        # Visit children to find flow_steps, match_exprs, etc.
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.Field_defContext, GASDParser.Match_exprContext)):
                res = self.visit(child)
                if res:
                    steps.append(res)
                    
        return FlowDefinition(name=name, parameters=params, steps=steps, returnType=ret, annotations=anns, **loc)
    def visitFlow_step(self, ctx: GASDParser.Flow_stepContext):
        loc = self._get_loc(ctx)
        
        if hasattr(ctx, 'annotations') and ctx.annotations():
            anns = self.visit(ctx.annotations())
            if anns:
                self.pending_annotations.extend(anns)
        
        step_num = None
        step_id_ctx = None
        
        if hasattr(ctx, 'step_id'):
            step_id_val = ctx.step_id()
            if isinstance(step_id_val, list):
                if len(step_id_val) > 0:
                    step_id_ctx = step_id_val[0]
            else:
                step_id_ctx = step_id_val
                
        if step_id_ctx:
            step_num_str = step_id_ctx.getText()
            if "." in step_num_str:
                 # Extract first component for backward compatibility with int stepNumber
                 try:
                     step_num = int(step_num_str.split('.')[0])
                 except:
                     step_num = None
            else:
                 try:
                     step_num = int(step_num_str)
                 except:
                     step_num = None
        
        main_op = None
        if ctx.control_flow():
            main_op = self.visit(ctx.control_flow())
        elif ctx.action():
            main_op = self.visit(ctx.action())
        elif ctx.match_expr():
            main_op = self.visit(ctx.match_expr())
            
        deps = []
        if ctx.depends_clause():
            deps = [r.getText().replace("STEP", "").strip() for r in ctx.depends_clause().step_ref()]

        res = None
        if isinstance(main_op, (MatchNode, EnsureNode)):
            res = main_op
        elif main_op:
            # Op is a dict from visitAction or visitControl_flow
            res = FlowStepNode(
                stepNumber=step_num,
                action=main_op.get("action", ""),
                target=main_op.get("target", ""),
                dependsOn=deps,
                postconditions=main_op.get("postconditions", []),
                timeout=main_op.get("timeout"),
                asBinding=main_op.get("asBinding"),
                typePath=main_op.get("typePath"),
                subSteps=main_op.get("subSteps", []),
                **loc
            )
        else:
            # Actionless step (only step_id or internal_block)
            res = FlowStepNode(
                stepNumber=step_num,
                action="",
                target="",
                dependsOn=deps,
                **loc
            )

        # Handle internal_block content for properties/dependencies
        if ctx.internal_block():
            block_items = self.visit(ctx.internal_block())
            for item in block_items:
                if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str) and item[0] == "DEPENDS":
                    res.dependsOn.extend(item[1:])
                elif isinstance(item, list) and len(item) > 0 and isinstance(item[0], str) and item[0] == "POSTCONDITION":
                    res.postconditions.extend(item[1:])
                elif isinstance(item, list) and len(item) > 0 and isinstance(item[0], str) and item[0] == "TIMEOUT":
                    res.timeout = item[1]
                elif isinstance(item, FlowStepNode):
                    if getattr(res, 'subSteps', None) is None: res.subSteps = []
                    res.subSteps.append(item)

        if self.pending_annotations and res:
            res.annotations = self.pending_annotations
            self.pending_annotations = []
            
        if res and getattr(res, 'action', None) == "" and len(getattr(res, 'annotations', [])) > 0 and getattr(res, 'stepNumber', None) is None:
            res.action = "ANNOTATION"
            
        return res

    def visitInternal_block(self, ctx: GASDParser.Internal_blockContext):
        items = []
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, (GASDParser.Flow_stepContext, GASDParser.Step_propertyContext, 
                                 GASDParser.Otherwise_stmtContext, GASDParser.Depends_stmtContext,
                                 GASDParser.Postcondition_stmtContext, GASDParser.Timeout_stmtContext)):
                res = self.visit(child)
                if res: items.append(res)
        return items

    def visitDepends_stmt(self, ctx: GASDParser.Depends_stmtContext):
        deps = [r.getText().replace("STEP", "").strip().strip("'") for r in ctx.depends_clause().step_ref()]
        return ["DEPENDS"] + deps

    def visitPostcondition_stmt(self, ctx: GASDParser.Postcondition_stmtContext):
        pcs = [pe.getText() for pe in ctx.postcondition_expr()]
        return ["POSTCONDITION"] + pcs

    def visitTimeout_stmt(self, ctx: GASDParser.Timeout_stmtContext):
        return ["TIMEOUT", ctx.duration_literal().getText()]

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
        action_name = ""
        # Get action name - handle all possible keywords
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            # Find the first keyword child (usually at index 0 or after annotations)
            from antlr4.tree.Tree import TerminalNodeImpl
            if isinstance(child, TerminalNodeImpl):
                text = child.getText()
                if text.isupper(): # Basic heuristic for keywords
                    action_name = text
                    break

        target = ""
        postconditions = []
        timeout = None

        as_binding = None
        type_path = None

        if ctx.VALIDATE_KW():
            target = self._get_text(ctx.expr(), 0)
            # Populate AS TYPE binding for VALIDATE actions
            if ctx.AS_KW() and ctx.TYPE_KW():
                as_binding = "AS TYPE"
                # Extract the type path from dot-separated soft_ids after TYPE
                found_type = False
                for i in range(ctx.getChildCount()):
                    child = ctx.getChild(i)
                    text = child.getText()
                    if text == "TYPE":
                        found_type = True
                        continue
                    if found_type:
                        if isinstance(child, GASDParser.Type_exprContext):
                            type_path = text
                            break
                        elif text == ".":
                            continue
                        elif isinstance(child, GASDParser.Soft_idContext):
                            type_path = text
                            break
                        else:
                            break
        elif ctx.ACHIEVE_KW():
            sl = ctx.STRING_LITERAL()
            if not sl:
                sl = ctx.soft_id()
            
            if isinstance(sl, list):
                # Join multi-part ACHIEVE 'A' AND 'B' targets
                parts = []
                for s in sl:
                    parts.append(s.getText().strip('"\''))
                target = " AND ".join(parts)
            else:
                target = sl.getText().strip('"\'') if sl else ""
            
            # Inline version: ACHIEVE 'Task': expr
            if hasattr(ctx, 'postcondition_expr') and ctx.postcondition_expr():
                pc_text = ctx.postcondition_expr().getText()
                postconditions.append(pc_text)
            # Indented blocks are now handled by visitFlow_step's internal_block check
        elif ctx.CREATE_KW() or ctx.RETURN_KW() or ctx.LOG_KW() or ctx.THROW_KW() or ctx.UPDATE_KW():
            # For these, the target is the rest of the line content
            # Reconstruct target from children excluding keywords and punctuation
            parts = []
            for i in range(1, ctx.getChildCount()):
                child = ctx.getChild(i)
                if not isinstance(child, (GASDParser.AnnotationsContext, GASDParser.Internal_blockContext)):
                     parts.append(child.getText())
            target = " ".join(parts).strip()
        elif ctx.PERSIST_KW():
            target = ctx.expr(0).getText() if ctx.expr(0) else ""
            if ctx.VIA_KW() and len(ctx.expr()) > 1: target += f" via {ctx.expr(1).getText()}"
        else:
            # generic action
            parts = []
            for i in range(1, ctx.getChildCount()):
                parts.append(ctx.getChild(i).getText())
            target = " ".join(parts).strip()
        
        return {
            "action": action_name, 
            "target": target, 
            "postconditions": postconditions,
            "timeout": timeout,
            "asBinding": as_binding,
            "typePath": type_path
        }

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

    def visitAnnotations(self, ctx: GASDParser.AnnotationsContext):
        return [self.visit(a) for a in ctx.annotation()]

    def visitValue_list(self, ctx: GASDParser.Value_listContext):
        from antlr4.tree.Tree import TerminalNodeImpl
        args = []
        # value_list : (value | named_arg) ( (COMMA)? (value | named_arg))*
        for i in range(ctx.getChildCount()):
            child = ctx.getChild(i)
            if isinstance(child, TerminalNodeImpl):
                continue # Skip commas
            
            res = self.visit(child)
            if isinstance(res, AnnotationArg):
                args.append(res)
            elif res is not None:
                # Simple value from visitValue
                args.append(AnnotationArg(value=str(res)))
        return args

    def visitNamed_arg(self, ctx: GASDParser.Named_argContext):
        key = ctx.soft_id().getText()
        val = self.visit(ctx.value())
        return AnnotationArg(value=str(val), key=key)

    def visitAnnotation(self, ctx: GASDParser.AnnotationContext):
        # name=soft_id
        name = ctx.name.getText() if ctx.name else ""
        args = []
        if hasattr(ctx, 'args') and ctx.args:
            args = self.visit(ctx.args)
        elif hasattr(ctx, 'param_id') and ctx.param_id:
            args = [AnnotationArg(value=ctx.param_id.getText().strip('"\''))]
            
        alias = ctx.alias.getText().strip('"\'') if ctx.AS_KW() and ctx.alias else None
        
        return Annotation(name=name, arguments=args, alias=alias)

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

    def visitContract_def(self, ctx: GASDParser.Contract_defContext):
        loc = self._get_loc(ctx)
        
        # Handle either qualified_name or STRING_LITERAL
        name = ""
        if ctx.qualified_name():
            name = ctx.qualified_name().getText()
        elif ctx.STRING_LITERAL():
            name = ctx.STRING_LITERAL().getText().strip('"\'')
            
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        
        inputs = self.visit(ctx.input_blk()) if ctx.input_blk() else []
        output = self.visit(ctx.output_blk()) if ctx.output_blk() else None
        
        cases = {}
        for cblk in ctx.case_blk():
            case_node = self.visit(cblk)
            cases[case_node.name] = case_node
            
        idem = False
        if ctx.idempotent_blk():
            idem = ctx.idempotent_blk().BOOLEAN_LITERAL().getText().lower() == "true"
            
        ver = None
        if ctx.version_dir():
             ver = ctx.version_dir().getChild(1).getText().strip('"\'')

        return ContractDefinition(name=name, inputs=inputs, output=output, behaviors=cases, idempotent=idem, version=ver, annotations=anns, **loc)

    def visitInput_blk(self, ctx: GASDParser.Input_blkContext):
        if ctx.param_list():
            return self.visit(ctx.param_list())
        return [self.visit(p) for p in ctx.param()]

    def visitOutput_blk(self, ctx: GASDParser.Output_blkContext):
        return self.visit(ctx.type_expr())

    def visitCase_blk(self, ctx: GASDParser.Case_blkContext):
        loc = self._get_loc(ctx)
        name = ""
        if ctx.soft_id():
            name = ctx.soft_id().getText()
        elif ctx.STRING_LITERAL():
            name = ctx.STRING_LITERAL().getText().strip('"\'')
            
        clauses = []
        for c in ctx.case_clause():
            clauses.append(self.visit(c))
        return ContractCase(name=name, clauses=clauses, **loc)

    def visitCase_clause(self, ctx: GASDParser.Case_clauseContext):
        res = {}
        if ctx.POSTCONDITION_KW():
            res["type"] = "POSTCONDITION"
            res["value"] = ctx.postcondition_expr().getText()
        elif ctx.THROWS_KW():
            res["type"] = "THROWS"
            res["value"] = ctx.soft_id().getText()
        elif ctx.AFTER_KW():
            res["type"] = "AFTER"
            res["value"] = ctx.getChild(2).getText()
        return res

    def visitModel_def(self, ctx: GASDParser.Model_defContext):
        loc = self._get_loc(ctx)
        name = ctx.STRING_LITERAL(0).getText().strip('"\'')
        model_type = ctx.tech_id().getText() if ctx.tech_id() else "Unknown"
        file_path = ctx.STRING_LITERAL(1).getText().strip('"\'')
        verifies = []
        if ctx.VERIFIES_KW():
            for ir in ctx.invariant_ref():
                scope = "GLOBAL"
                if "LOCAL" in ir.getText(): scope = "LOCAL"
                elif "GLOBAL" in ir.getText(): scope = "GLOBAL"
                verifies.append(f"{scope} {ir.STRING_LITERAL().getText()}")
        assumptions = []
        if ctx.ASSUMPTIONS_KW():
            assumptions = [a.getText().strip('"\'') for a in ctx.STRING_LITERAL()[2:]] # Skip first name and path
        
        return ModelDefinition(name=name, type=model_type, file=file_path, verifies=verifies, assumptions=assumptions, **loc)

    def visitAssumption_def(self, ctx: GASDParser.Assumption_defContext):
        loc = self._get_loc(ctx)
        sl = ctx.STRING_LITERAL()
        if ctx.soft_id():
            name = ctx.soft_id().getText()
        else:
            name = sl[0].getText().strip('"\'') if sl else "Unknown"
        
        affects = []
        if ctx.AFFECTS_KW() and ctx.list_literal():
            for v in ctx.list_literal().value():
                affects.append(v.getText().strip('"\''))
        
        consequence = None
        if ctx.CONSEQUENCE_KW() and sl:
            consequence = sl[-1].getText().strip('"\'')
        
        return AssumptionDefinition(name=name, affects=affects, consequence=consequence, **loc)

    def visitConstraint_stmt(self, ctx: GASDParser.Constraint_stmtContext):
        name = None
        text = ""
        str_literals = ctx.STRING_LITERAL()
        
        if ctx.expr():
            text = ctx.expr().getText().strip('"\'')
            if ctx.soft_id(): name = ctx.soft_id().getText()
            elif str_literals: name = str_literals[0].getText().strip('"\'')
        else:
            if len(str_literals) == 2:
                name = str_literals[0].getText().strip('"\'')
                text = str_literals[1].getText().strip('"\'')
            elif len(str_literals) == 1:
                if ctx.soft_id():
                    name = ctx.soft_id().getText()
                text = str_literals[0].getText().strip('"\'')
        
        return ConstraintNode(kind="Constraint", text=text, name=name, **self._get_loc(ctx))

    def visitInvariant_stmt(self, ctx: GASDParser.Invariant_stmtContext):
        scope = None
        full_text = ctx.getText()
        if ctx.GLOBAL_KW() or "GLOBAL" in full_text: scope = "GLOBAL"
        elif ctx.LOCAL_KW() or "LOCAL" in full_text: scope = "LOCAL"
        
        name = None
        text = ""
        str_literals = ctx.STRING_LITERAL()
        
        if ctx.expr():
            text = ctx.expr().getText().strip('"\'')
            if ctx.soft_id(): name = ctx.soft_id().getText()
            elif str_literals: name = str_literals[0].getText().strip('"\'')
        else:
            if len(str_literals) == 2:
                name = str_literals[0].getText().strip('"\'')
                text = str_literals[1].getText().strip('"\'')
            elif len(str_literals) == 1:
                if ctx.soft_id():
                    name = ctx.soft_id().getText()
                text = str_literals[0].getText().strip('"\'')
        
        return ConstraintNode(
            text=text,
            kind="Invariant",
            name=name,
            scope=scope,
            **self._get_loc(ctx)
        )

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
        anns = self.pending_annotations + self._visit_anns(ctx.annotations())
        self.pending_annotations = []
        
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

        return StrategyDefinition(name=name, algorithm=algo, precondition=prec, complexity=comp, inputs=inputs, output=output, annotations=anns, **loc)


    def _visit_anns(self, ctx_list):
        if not ctx_list: return []
        if isinstance(ctx_list, list):
            res = []
            for c in ctx_list:
                res.extend(self.visit(c))
            return res
        return self.visit(ctx_list)
