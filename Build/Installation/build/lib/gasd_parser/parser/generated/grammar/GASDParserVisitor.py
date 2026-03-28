# Generated from Impl/grammar/GASDParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .GASDParser import GASDParser
else:
    from GASDParser import GASDParser

# This class defines a complete generic visitor for a parse tree produced by GASDParser.

class GASDParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by GASDParser#gasd_file.
    def visitGasd_file(self, ctx:GASDParser.Gasd_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#section.
    def visitSection(self, ctx:GASDParser.SectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#version_dir.
    def visitVersion_dir(self, ctx:GASDParser.Version_dirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#version_number.
    def visitVersion_number(self, ctx:GASDParser.Version_numberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#context_dir.
    def visitContext_dir(self, ctx:GASDParser.Context_dirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#target_dir.
    def visitTarget_dir(self, ctx:GASDParser.Target_dirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#trace_dir.
    def visitTrace_dir(self, ctx:GASDParser.Trace_dirContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#namespace_stmt.
    def visitNamespace_stmt(self, ctx:GASDParser.Namespace_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#import_stmt.
    def visitImport_stmt(self, ctx:GASDParser.Import_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#decision_blk.
    def visitDecision_blk(self, ctx:GASDParser.Decision_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#type_def.
    def visitType_def(self, ctx:GASDParser.Type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#field_def.
    def visitField_def(self, ctx:GASDParser.Field_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#type_expr.
    def visitType_expr(self, ctx:GASDParser.Type_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#component_def.
    def visitComponent_def(self, ctx:GASDParser.Component_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#component_body_item.
    def visitComponent_body_item(self, ctx:GASDParser.Component_body_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#bullet_item.
    def visitBullet_item(self, ctx:GASDParser.Bullet_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#method_sig.
    def visitMethod_sig(self, ctx:GASDParser.Method_sigContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#param_list.
    def visitParam_list(self, ctx:GASDParser.Param_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#param.
    def visitParam(self, ctx:GASDParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#flow_def.
    def visitFlow_def(self, ctx:GASDParser.Flow_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#flow_step.
    def visitFlow_step(self, ctx:GASDParser.Flow_stepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#step_id.
    def visitStep_id(self, ctx:GASDParser.Step_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#depends_clause.
    def visitDepends_clause(self, ctx:GASDParser.Depends_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#depends_stmt.
    def visitDepends_stmt(self, ctx:GASDParser.Depends_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#step_ref.
    def visitStep_ref(self, ctx:GASDParser.Step_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#internal_block.
    def visitInternal_block(self, ctx:GASDParser.Internal_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#otherwise_stmt.
    def visitOtherwise_stmt(self, ctx:GASDParser.Otherwise_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#postcondition_stmt.
    def visitPostcondition_stmt(self, ctx:GASDParser.Postcondition_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#postcondition_expr.
    def visitPostcondition_expr(self, ctx:GASDParser.Postcondition_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#timeout_stmt.
    def visitTimeout_stmt(self, ctx:GASDParser.Timeout_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#duration_literal.
    def visitDuration_literal(self, ctx:GASDParser.Duration_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#on_error_clause.
    def visitOn_error_clause(self, ctx:GASDParser.On_error_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#step_property.
    def visitStep_property(self, ctx:GASDParser.Step_propertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#permissive_token.
    def visitPermissive_token(self, ctx:GASDParser.Permissive_tokenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#action.
    def visitAction(self, ctx:GASDParser.ActionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#action_id.
    def visitAction_id(self, ctx:GASDParser.Action_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#control_flow.
    def visitControl_flow(self, ctx:GASDParser.Control_flowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#match_section.
    def visitMatch_section(self, ctx:GASDParser.Match_sectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#match_expr.
    def visitMatch_expr(self, ctx:GASDParser.Match_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#match_case.
    def visitMatch_case(self, ctx:GASDParser.Match_caseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#match_pattern.
    def visitMatch_pattern(self, ctx:GASDParser.Match_patternContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#match_case_block_items.
    def visitMatch_case_block_items(self, ctx:GASDParser.Match_case_block_itemsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#ensure_stmt.
    def visitEnsure_stmt(self, ctx:GASDParser.Ensure_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#strategy_def.
    def visitStrategy_def(self, ctx:GASDParser.Strategy_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#strategy_item.
    def visitStrategy_item(self, ctx:GASDParser.Strategy_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#constraint_stmt.
    def visitConstraint_stmt(self, ctx:GASDParser.Constraint_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#invariant_stmt.
    def visitInvariant_stmt(self, ctx:GASDParser.Invariant_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#contract_def.
    def visitContract_def(self, ctx:GASDParser.Contract_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#input_blk.
    def visitInput_blk(self, ctx:GASDParser.Input_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#output_blk.
    def visitOutput_blk(self, ctx:GASDParser.Output_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#idempotent_blk.
    def visitIdempotent_blk(self, ctx:GASDParser.Idempotent_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#case_blk.
    def visitCase_blk(self, ctx:GASDParser.Case_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#case_clause.
    def visitCase_clause(self, ctx:GASDParser.Case_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#model_def.
    def visitModel_def(self, ctx:GASDParser.Model_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#invariant_ref.
    def visitInvariant_ref(self, ctx:GASDParser.Invariant_refContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#assumption_def.
    def visitAssumption_def(self, ctx:GASDParser.Assumption_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#qualified_name.
    def visitQualified_name(self, ctx:GASDParser.Qualified_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#question_stmt.
    def visitQuestion_stmt(self, ctx:GASDParser.Question_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#approve_blk.
    def visitApprove_blk(self, ctx:GASDParser.Approve_blkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#todo_stmt.
    def visitTodo_stmt(self, ctx:GASDParser.Todo_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#review_stmt.
    def visitReview_stmt(self, ctx:GASDParser.Review_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#value.
    def visitValue(self, ctx:GASDParser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#value_list.
    def visitValue_list(self, ctx:GASDParser.Value_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#named_arg.
    def visitNamed_arg(self, ctx:GASDParser.Named_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#base_value.
    def visitBase_value(self, ctx:GASDParser.Base_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#list_literal.
    def visitList_literal(self, ctx:GASDParser.List_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#map_literal.
    def visitMap_literal(self, ctx:GASDParser.Map_literalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#map_entry.
    def visitMap_entry(self, ctx:GASDParser.Map_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#ValueExpr.
    def visitValueExpr(self, ctx:GASDParser.ValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#ArithmeticExpr.
    def visitArithmeticExpr(self, ctx:GASDParser.ArithmeticExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#ComparisonExpr.
    def visitComparisonExpr(self, ctx:GASDParser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#NotExpr.
    def visitNotExpr(self, ctx:GASDParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#ParenExpr.
    def visitParenExpr(self, ctx:GASDParser.ParenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#LogicalExpr.
    def visitLogicalExpr(self, ctx:GASDParser.LogicalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#comparison_op.
    def visitComparison_op(self, ctx:GASDParser.Comparison_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#annotations.
    def visitAnnotations(self, ctx:GASDParser.AnnotationsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#annotation.
    def visitAnnotation(self, ctx:GASDParser.AnnotationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#param_val.
    def visitParam_val(self, ctx:GASDParser.Param_valContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#alias_val.
    def visitAlias_val(self, ctx:GASDParser.Alias_valContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GASDParser#soft_id.
    def visitSoft_id(self, ctx:GASDParser.Soft_idContext):
        return self.visitChildren(ctx)



del GASDParser