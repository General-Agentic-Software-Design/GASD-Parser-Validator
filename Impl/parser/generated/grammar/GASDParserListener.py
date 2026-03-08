# Generated from GASDParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .GASDParser import GASDParser
else:
    from GASDParser import GASDParser

# This class defines a complete listener for a parse tree produced by GASDParser.
class GASDParserListener(ParseTreeListener):

    # Enter a parse tree produced by GASDParser#gasd_file.
    def enterGasd_file(self, ctx:GASDParser.Gasd_fileContext):
        pass

    # Exit a parse tree produced by GASDParser#gasd_file.
    def exitGasd_file(self, ctx:GASDParser.Gasd_fileContext):
        pass


    # Enter a parse tree produced by GASDParser#section.
    def enterSection(self, ctx:GASDParser.SectionContext):
        pass

    # Exit a parse tree produced by GASDParser#section.
    def exitSection(self, ctx:GASDParser.SectionContext):
        pass


    # Enter a parse tree produced by GASDParser#context_dir.
    def enterContext_dir(self, ctx:GASDParser.Context_dirContext):
        pass

    # Exit a parse tree produced by GASDParser#context_dir.
    def exitContext_dir(self, ctx:GASDParser.Context_dirContext):
        pass


    # Enter a parse tree produced by GASDParser#target_dir.
    def enterTarget_dir(self, ctx:GASDParser.Target_dirContext):
        pass

    # Exit a parse tree produced by GASDParser#target_dir.
    def exitTarget_dir(self, ctx:GASDParser.Target_dirContext):
        pass


    # Enter a parse tree produced by GASDParser#trace_dir.
    def enterTrace_dir(self, ctx:GASDParser.Trace_dirContext):
        pass

    # Exit a parse tree produced by GASDParser#trace_dir.
    def exitTrace_dir(self, ctx:GASDParser.Trace_dirContext):
        pass


    # Enter a parse tree produced by GASDParser#namespace_stmt.
    def enterNamespace_stmt(self, ctx:GASDParser.Namespace_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#namespace_stmt.
    def exitNamespace_stmt(self, ctx:GASDParser.Namespace_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#import_stmt.
    def enterImport_stmt(self, ctx:GASDParser.Import_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#import_stmt.
    def exitImport_stmt(self, ctx:GASDParser.Import_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#decision_blk.
    def enterDecision_blk(self, ctx:GASDParser.Decision_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#decision_blk.
    def exitDecision_blk(self, ctx:GASDParser.Decision_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#type_def.
    def enterType_def(self, ctx:GASDParser.Type_defContext):
        pass

    # Exit a parse tree produced by GASDParser#type_def.
    def exitType_def(self, ctx:GASDParser.Type_defContext):
        pass


    # Enter a parse tree produced by GASDParser#field_def.
    def enterField_def(self, ctx:GASDParser.Field_defContext):
        pass

    # Exit a parse tree produced by GASDParser#field_def.
    def exitField_def(self, ctx:GASDParser.Field_defContext):
        pass


    # Enter a parse tree produced by GASDParser#type_expr.
    def enterType_expr(self, ctx:GASDParser.Type_exprContext):
        pass

    # Exit a parse tree produced by GASDParser#type_expr.
    def exitType_expr(self, ctx:GASDParser.Type_exprContext):
        pass


    # Enter a parse tree produced by GASDParser#component_def.
    def enterComponent_def(self, ctx:GASDParser.Component_defContext):
        pass

    # Exit a parse tree produced by GASDParser#component_def.
    def exitComponent_def(self, ctx:GASDParser.Component_defContext):
        pass


    # Enter a parse tree produced by GASDParser#component_body_item.
    def enterComponent_body_item(self, ctx:GASDParser.Component_body_itemContext):
        pass

    # Exit a parse tree produced by GASDParser#component_body_item.
    def exitComponent_body_item(self, ctx:GASDParser.Component_body_itemContext):
        pass


    # Enter a parse tree produced by GASDParser#bullet_item.
    def enterBullet_item(self, ctx:GASDParser.Bullet_itemContext):
        pass

    # Exit a parse tree produced by GASDParser#bullet_item.
    def exitBullet_item(self, ctx:GASDParser.Bullet_itemContext):
        pass


    # Enter a parse tree produced by GASDParser#method_sig.
    def enterMethod_sig(self, ctx:GASDParser.Method_sigContext):
        pass

    # Exit a parse tree produced by GASDParser#method_sig.
    def exitMethod_sig(self, ctx:GASDParser.Method_sigContext):
        pass


    # Enter a parse tree produced by GASDParser#param_list.
    def enterParam_list(self, ctx:GASDParser.Param_listContext):
        pass

    # Exit a parse tree produced by GASDParser#param_list.
    def exitParam_list(self, ctx:GASDParser.Param_listContext):
        pass


    # Enter a parse tree produced by GASDParser#param.
    def enterParam(self, ctx:GASDParser.ParamContext):
        pass

    # Exit a parse tree produced by GASDParser#param.
    def exitParam(self, ctx:GASDParser.ParamContext):
        pass


    # Enter a parse tree produced by GASDParser#flow_def.
    def enterFlow_def(self, ctx:GASDParser.Flow_defContext):
        pass

    # Exit a parse tree produced by GASDParser#flow_def.
    def exitFlow_def(self, ctx:GASDParser.Flow_defContext):
        pass


    # Enter a parse tree produced by GASDParser#flow_step.
    def enterFlow_step(self, ctx:GASDParser.Flow_stepContext):
        pass

    # Exit a parse tree produced by GASDParser#flow_step.
    def exitFlow_step(self, ctx:GASDParser.Flow_stepContext):
        pass


    # Enter a parse tree produced by GASDParser#internal_block.
    def enterInternal_block(self, ctx:GASDParser.Internal_blockContext):
        pass

    # Exit a parse tree produced by GASDParser#internal_block.
    def exitInternal_block(self, ctx:GASDParser.Internal_blockContext):
        pass


    # Enter a parse tree produced by GASDParser#otherwise_stmt.
    def enterOtherwise_stmt(self, ctx:GASDParser.Otherwise_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#otherwise_stmt.
    def exitOtherwise_stmt(self, ctx:GASDParser.Otherwise_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#step_property.
    def enterStep_property(self, ctx:GASDParser.Step_propertyContext):
        pass

    # Exit a parse tree produced by GASDParser#step_property.
    def exitStep_property(self, ctx:GASDParser.Step_propertyContext):
        pass


    # Enter a parse tree produced by GASDParser#permissive_token.
    def enterPermissive_token(self, ctx:GASDParser.Permissive_tokenContext):
        pass

    # Exit a parse tree produced by GASDParser#permissive_token.
    def exitPermissive_token(self, ctx:GASDParser.Permissive_tokenContext):
        pass


    # Enter a parse tree produced by GASDParser#action.
    def enterAction(self, ctx:GASDParser.ActionContext):
        pass

    # Exit a parse tree produced by GASDParser#action.
    def exitAction(self, ctx:GASDParser.ActionContext):
        pass


    # Enter a parse tree produced by GASDParser#control_flow.
    def enterControl_flow(self, ctx:GASDParser.Control_flowContext):
        pass

    # Exit a parse tree produced by GASDParser#control_flow.
    def exitControl_flow(self, ctx:GASDParser.Control_flowContext):
        pass


    # Enter a parse tree produced by GASDParser#match_section.
    def enterMatch_section(self, ctx:GASDParser.Match_sectionContext):
        pass

    # Exit a parse tree produced by GASDParser#match_section.
    def exitMatch_section(self, ctx:GASDParser.Match_sectionContext):
        pass


    # Enter a parse tree produced by GASDParser#match_expr.
    def enterMatch_expr(self, ctx:GASDParser.Match_exprContext):
        pass

    # Exit a parse tree produced by GASDParser#match_expr.
    def exitMatch_expr(self, ctx:GASDParser.Match_exprContext):
        pass


    # Enter a parse tree produced by GASDParser#match_case.
    def enterMatch_case(self, ctx:GASDParser.Match_caseContext):
        pass

    # Exit a parse tree produced by GASDParser#match_case.
    def exitMatch_case(self, ctx:GASDParser.Match_caseContext):
        pass


    # Enter a parse tree produced by GASDParser#match_pattern.
    def enterMatch_pattern(self, ctx:GASDParser.Match_patternContext):
        pass

    # Exit a parse tree produced by GASDParser#match_pattern.
    def exitMatch_pattern(self, ctx:GASDParser.Match_patternContext):
        pass


    # Enter a parse tree produced by GASDParser#match_case_block_items.
    def enterMatch_case_block_items(self, ctx:GASDParser.Match_case_block_itemsContext):
        pass

    # Exit a parse tree produced by GASDParser#match_case_block_items.
    def exitMatch_case_block_items(self, ctx:GASDParser.Match_case_block_itemsContext):
        pass


    # Enter a parse tree produced by GASDParser#ensure_stmt.
    def enterEnsure_stmt(self, ctx:GASDParser.Ensure_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#ensure_stmt.
    def exitEnsure_stmt(self, ctx:GASDParser.Ensure_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#strategy_def.
    def enterStrategy_def(self, ctx:GASDParser.Strategy_defContext):
        pass

    # Exit a parse tree produced by GASDParser#strategy_def.
    def exitStrategy_def(self, ctx:GASDParser.Strategy_defContext):
        pass


    # Enter a parse tree produced by GASDParser#strategy_item.
    def enterStrategy_item(self, ctx:GASDParser.Strategy_itemContext):
        pass

    # Exit a parse tree produced by GASDParser#strategy_item.
    def exitStrategy_item(self, ctx:GASDParser.Strategy_itemContext):
        pass


    # Enter a parse tree produced by GASDParser#constraint_stmt.
    def enterConstraint_stmt(self, ctx:GASDParser.Constraint_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#constraint_stmt.
    def exitConstraint_stmt(self, ctx:GASDParser.Constraint_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#invariant_stmt.
    def enterInvariant_stmt(self, ctx:GASDParser.Invariant_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#invariant_stmt.
    def exitInvariant_stmt(self, ctx:GASDParser.Invariant_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#question_stmt.
    def enterQuestion_stmt(self, ctx:GASDParser.Question_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#question_stmt.
    def exitQuestion_stmt(self, ctx:GASDParser.Question_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#approve_blk.
    def enterApprove_blk(self, ctx:GASDParser.Approve_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#approve_blk.
    def exitApprove_blk(self, ctx:GASDParser.Approve_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#todo_stmt.
    def enterTodo_stmt(self, ctx:GASDParser.Todo_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#todo_stmt.
    def exitTodo_stmt(self, ctx:GASDParser.Todo_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#review_stmt.
    def enterReview_stmt(self, ctx:GASDParser.Review_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#review_stmt.
    def exitReview_stmt(self, ctx:GASDParser.Review_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#value.
    def enterValue(self, ctx:GASDParser.ValueContext):
        pass

    # Exit a parse tree produced by GASDParser#value.
    def exitValue(self, ctx:GASDParser.ValueContext):
        pass


    # Enter a parse tree produced by GASDParser#value_list.
    def enterValue_list(self, ctx:GASDParser.Value_listContext):
        pass

    # Exit a parse tree produced by GASDParser#value_list.
    def exitValue_list(self, ctx:GASDParser.Value_listContext):
        pass


    # Enter a parse tree produced by GASDParser#named_arg.
    def enterNamed_arg(self, ctx:GASDParser.Named_argContext):
        pass

    # Exit a parse tree produced by GASDParser#named_arg.
    def exitNamed_arg(self, ctx:GASDParser.Named_argContext):
        pass


    # Enter a parse tree produced by GASDParser#base_value.
    def enterBase_value(self, ctx:GASDParser.Base_valueContext):
        pass

    # Exit a parse tree produced by GASDParser#base_value.
    def exitBase_value(self, ctx:GASDParser.Base_valueContext):
        pass


    # Enter a parse tree produced by GASDParser#list_literal.
    def enterList_literal(self, ctx:GASDParser.List_literalContext):
        pass

    # Exit a parse tree produced by GASDParser#list_literal.
    def exitList_literal(self, ctx:GASDParser.List_literalContext):
        pass


    # Enter a parse tree produced by GASDParser#map_literal.
    def enterMap_literal(self, ctx:GASDParser.Map_literalContext):
        pass

    # Exit a parse tree produced by GASDParser#map_literal.
    def exitMap_literal(self, ctx:GASDParser.Map_literalContext):
        pass


    # Enter a parse tree produced by GASDParser#map_entry.
    def enterMap_entry(self, ctx:GASDParser.Map_entryContext):
        pass

    # Exit a parse tree produced by GASDParser#map_entry.
    def exitMap_entry(self, ctx:GASDParser.Map_entryContext):
        pass


    # Enter a parse tree produced by GASDParser#ValueExpr.
    def enterValueExpr(self, ctx:GASDParser.ValueExprContext):
        pass

    # Exit a parse tree produced by GASDParser#ValueExpr.
    def exitValueExpr(self, ctx:GASDParser.ValueExprContext):
        pass


    # Enter a parse tree produced by GASDParser#ArithmeticExpr.
    def enterArithmeticExpr(self, ctx:GASDParser.ArithmeticExprContext):
        pass

    # Exit a parse tree produced by GASDParser#ArithmeticExpr.
    def exitArithmeticExpr(self, ctx:GASDParser.ArithmeticExprContext):
        pass


    # Enter a parse tree produced by GASDParser#ComparisonExpr.
    def enterComparisonExpr(self, ctx:GASDParser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by GASDParser#ComparisonExpr.
    def exitComparisonExpr(self, ctx:GASDParser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by GASDParser#NotExpr.
    def enterNotExpr(self, ctx:GASDParser.NotExprContext):
        pass

    # Exit a parse tree produced by GASDParser#NotExpr.
    def exitNotExpr(self, ctx:GASDParser.NotExprContext):
        pass


    # Enter a parse tree produced by GASDParser#ParenExpr.
    def enterParenExpr(self, ctx:GASDParser.ParenExprContext):
        pass

    # Exit a parse tree produced by GASDParser#ParenExpr.
    def exitParenExpr(self, ctx:GASDParser.ParenExprContext):
        pass


    # Enter a parse tree produced by GASDParser#LogicalExpr.
    def enterLogicalExpr(self, ctx:GASDParser.LogicalExprContext):
        pass

    # Exit a parse tree produced by GASDParser#LogicalExpr.
    def exitLogicalExpr(self, ctx:GASDParser.LogicalExprContext):
        pass


    # Enter a parse tree produced by GASDParser#comparison_op.
    def enterComparison_op(self, ctx:GASDParser.Comparison_opContext):
        pass

    # Exit a parse tree produced by GASDParser#comparison_op.
    def exitComparison_op(self, ctx:GASDParser.Comparison_opContext):
        pass


    # Enter a parse tree produced by GASDParser#annotations.
    def enterAnnotations(self, ctx:GASDParser.AnnotationsContext):
        pass

    # Exit a parse tree produced by GASDParser#annotations.
    def exitAnnotations(self, ctx:GASDParser.AnnotationsContext):
        pass


    # Enter a parse tree produced by GASDParser#annotation.
    def enterAnnotation(self, ctx:GASDParser.AnnotationContext):
        pass

    # Exit a parse tree produced by GASDParser#annotation.
    def exitAnnotation(self, ctx:GASDParser.AnnotationContext):
        pass


    # Enter a parse tree produced by GASDParser#soft_id.
    def enterSoft_id(self, ctx:GASDParser.Soft_idContext):
        pass

    # Exit a parse tree produced by GASDParser#soft_id.
    def exitSoft_id(self, ctx:GASDParser.Soft_idContext):
        pass



del GASDParser