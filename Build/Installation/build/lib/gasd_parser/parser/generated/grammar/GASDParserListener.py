# Generated from Impl/grammar/GASDParser.g4 by ANTLR 4.13.2
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


    # Enter a parse tree produced by GASDParser#version_dir.
    def enterVersion_dir(self, ctx:GASDParser.Version_dirContext):
        pass

    # Exit a parse tree produced by GASDParser#version_dir.
    def exitVersion_dir(self, ctx:GASDParser.Version_dirContext):
        pass


    # Enter a parse tree produced by GASDParser#version_number.
    def enterVersion_number(self, ctx:GASDParser.Version_numberContext):
        pass

    # Exit a parse tree produced by GASDParser#version_number.
    def exitVersion_number(self, ctx:GASDParser.Version_numberContext):
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


    # Enter a parse tree produced by GASDParser#type_body_item.
    def enterType_body_item(self, ctx:GASDParser.Type_body_itemContext):
        pass

    # Exit a parse tree produced by GASDParser#type_body_item.
    def exitType_body_item(self, ctx:GASDParser.Type_body_itemContext):
        pass


    # Enter a parse tree produced by GASDParser#field_def.
    def enterField_def(self, ctx:GASDParser.Field_defContext):
        pass

    # Exit a parse tree produced by GASDParser#field_def.
    def exitField_def(self, ctx:GASDParser.Field_defContext):
        pass


    # Enter a parse tree produced by GASDParser#GenericType.
    def enterGenericType(self, ctx:GASDParser.GenericTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#GenericType.
    def exitGenericType(self, ctx:GASDParser.GenericTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#RecordType.
    def enterRecordType(self, ctx:GASDParser.RecordTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#RecordType.
    def exitRecordType(self, ctx:GASDParser.RecordTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#EnumType.
    def enterEnumType(self, ctx:GASDParser.EnumTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#EnumType.
    def exitEnumType(self, ctx:GASDParser.EnumTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#OptionalType.
    def enterOptionalType(self, ctx:GASDParser.OptionalTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#OptionalType.
    def exitOptionalType(self, ctx:GASDParser.OptionalTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#SimpleType.
    def enterSimpleType(self, ctx:GASDParser.SimpleTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#SimpleType.
    def exitSimpleType(self, ctx:GASDParser.SimpleTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#IntType.
    def enterIntType(self, ctx:GASDParser.IntTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#IntType.
    def exitIntType(self, ctx:GASDParser.IntTypeContext):
        pass


    # Enter a parse tree produced by GASDParser#FloatType.
    def enterFloatType(self, ctx:GASDParser.FloatTypeContext):
        pass

    # Exit a parse tree produced by GASDParser#FloatType.
    def exitFloatType(self, ctx:GASDParser.FloatTypeContext):
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


    # Enter a parse tree produced by GASDParser#step_id.
    def enterStep_id(self, ctx:GASDParser.Step_idContext):
        pass

    # Exit a parse tree produced by GASDParser#step_id.
    def exitStep_id(self, ctx:GASDParser.Step_idContext):
        pass


    # Enter a parse tree produced by GASDParser#depends_clause.
    def enterDepends_clause(self, ctx:GASDParser.Depends_clauseContext):
        pass

    # Exit a parse tree produced by GASDParser#depends_clause.
    def exitDepends_clause(self, ctx:GASDParser.Depends_clauseContext):
        pass


    # Enter a parse tree produced by GASDParser#depends_stmt.
    def enterDepends_stmt(self, ctx:GASDParser.Depends_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#depends_stmt.
    def exitDepends_stmt(self, ctx:GASDParser.Depends_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#step_ref.
    def enterStep_ref(self, ctx:GASDParser.Step_refContext):
        pass

    # Exit a parse tree produced by GASDParser#step_ref.
    def exitStep_ref(self, ctx:GASDParser.Step_refContext):
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


    # Enter a parse tree produced by GASDParser#postcondition_stmt.
    def enterPostcondition_stmt(self, ctx:GASDParser.Postcondition_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#postcondition_stmt.
    def exitPostcondition_stmt(self, ctx:GASDParser.Postcondition_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#postcondition_expr.
    def enterPostcondition_expr(self, ctx:GASDParser.Postcondition_exprContext):
        pass

    # Exit a parse tree produced by GASDParser#postcondition_expr.
    def exitPostcondition_expr(self, ctx:GASDParser.Postcondition_exprContext):
        pass


    # Enter a parse tree produced by GASDParser#timeout_stmt.
    def enterTimeout_stmt(self, ctx:GASDParser.Timeout_stmtContext):
        pass

    # Exit a parse tree produced by GASDParser#timeout_stmt.
    def exitTimeout_stmt(self, ctx:GASDParser.Timeout_stmtContext):
        pass


    # Enter a parse tree produced by GASDParser#duration_literal.
    def enterDuration_literal(self, ctx:GASDParser.Duration_literalContext):
        pass

    # Exit a parse tree produced by GASDParser#duration_literal.
    def exitDuration_literal(self, ctx:GASDParser.Duration_literalContext):
        pass


    # Enter a parse tree produced by GASDParser#on_error_clause.
    def enterOn_error_clause(self, ctx:GASDParser.On_error_clauseContext):
        pass

    # Exit a parse tree produced by GASDParser#on_error_clause.
    def exitOn_error_clause(self, ctx:GASDParser.On_error_clauseContext):
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


    # Enter a parse tree produced by GASDParser#action_id.
    def enterAction_id(self, ctx:GASDParser.Action_idContext):
        pass

    # Exit a parse tree produced by GASDParser#action_id.
    def exitAction_id(self, ctx:GASDParser.Action_idContext):
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


    # Enter a parse tree produced by GASDParser#contract_def.
    def enterContract_def(self, ctx:GASDParser.Contract_defContext):
        pass

    # Exit a parse tree produced by GASDParser#contract_def.
    def exitContract_def(self, ctx:GASDParser.Contract_defContext):
        pass


    # Enter a parse tree produced by GASDParser#input_blk.
    def enterInput_blk(self, ctx:GASDParser.Input_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#input_blk.
    def exitInput_blk(self, ctx:GASDParser.Input_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#output_blk.
    def enterOutput_blk(self, ctx:GASDParser.Output_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#output_blk.
    def exitOutput_blk(self, ctx:GASDParser.Output_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#idempotent_blk.
    def enterIdempotent_blk(self, ctx:GASDParser.Idempotent_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#idempotent_blk.
    def exitIdempotent_blk(self, ctx:GASDParser.Idempotent_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#case_blk.
    def enterCase_blk(self, ctx:GASDParser.Case_blkContext):
        pass

    # Exit a parse tree produced by GASDParser#case_blk.
    def exitCase_blk(self, ctx:GASDParser.Case_blkContext):
        pass


    # Enter a parse tree produced by GASDParser#case_clause.
    def enterCase_clause(self, ctx:GASDParser.Case_clauseContext):
        pass

    # Exit a parse tree produced by GASDParser#case_clause.
    def exitCase_clause(self, ctx:GASDParser.Case_clauseContext):
        pass


    # Enter a parse tree produced by GASDParser#model_def.
    def enterModel_def(self, ctx:GASDParser.Model_defContext):
        pass

    # Exit a parse tree produced by GASDParser#model_def.
    def exitModel_def(self, ctx:GASDParser.Model_defContext):
        pass


    # Enter a parse tree produced by GASDParser#invariant_ref.
    def enterInvariant_ref(self, ctx:GASDParser.Invariant_refContext):
        pass

    # Exit a parse tree produced by GASDParser#invariant_ref.
    def exitInvariant_ref(self, ctx:GASDParser.Invariant_refContext):
        pass


    # Enter a parse tree produced by GASDParser#assumption_def.
    def enterAssumption_def(self, ctx:GASDParser.Assumption_defContext):
        pass

    # Exit a parse tree produced by GASDParser#assumption_def.
    def exitAssumption_def(self, ctx:GASDParser.Assumption_defContext):
        pass


    # Enter a parse tree produced by GASDParser#qualified_name.
    def enterQualified_name(self, ctx:GASDParser.Qualified_nameContext):
        pass

    # Exit a parse tree produced by GASDParser#qualified_name.
    def exitQualified_name(self, ctx:GASDParser.Qualified_nameContext):
        pass


    # Enter a parse tree produced by GASDParser#tech_id.
    def enterTech_id(self, ctx:GASDParser.Tech_idContext):
        pass

    # Exit a parse tree produced by GASDParser#tech_id.
    def exitTech_id(self, ctx:GASDParser.Tech_idContext):
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


    # Enter a parse tree produced by GASDParser#primary_expr.
    def enterPrimary_expr(self, ctx:GASDParser.Primary_exprContext):
        pass

    # Exit a parse tree produced by GASDParser#primary_expr.
    def exitPrimary_expr(self, ctx:GASDParser.Primary_exprContext):
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


    # Enter a parse tree produced by GASDParser#param_val.
    def enterParam_val(self, ctx:GASDParser.Param_valContext):
        pass

    # Exit a parse tree produced by GASDParser#param_val.
    def exitParam_val(self, ctx:GASDParser.Param_valContext):
        pass


    # Enter a parse tree produced by GASDParser#alias_val.
    def enterAlias_val(self, ctx:GASDParser.Alias_valContext):
        pass

    # Exit a parse tree produced by GASDParser#alias_val.
    def exitAlias_val(self, ctx:GASDParser.Alias_valContext):
        pass


    # Enter a parse tree produced by GASDParser#soft_id.
    def enterSoft_id(self, ctx:GASDParser.Soft_idContext):
        pass

    # Exit a parse tree produced by GASDParser#soft_id.
    def exitSoft_id(self, ctx:GASDParser.Soft_idContext):
        pass



del GASDParser