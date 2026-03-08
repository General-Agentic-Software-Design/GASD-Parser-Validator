parser grammar GASDParser;

options {
    tokenVocab=GASDLexer;
}

// ===================================================================
// GASD File Structure
// ===================================================================

gasd_file
    : (NEWLINE)* (section)* EOF
    ;

section
    : context_dir
    | target_dir
    | trace_dir
    | namespace_stmt
    | import_stmt
    | decision_blk
    | type_def
    | component_def
    | flow_def
    | strategy_def
    | constraint_stmt
    | invariant_stmt
    | ensure_stmt
    | match_section
    | question_stmt
    | approve_blk
    | todo_stmt
    | review_stmt
    | annotations NEWLINE
    // Skip extra newlines between sections
    | NEWLINE
    ;

// ===================================================================
// Directives
// ===================================================================

context_dir     : CONTEXT_KW COLON value_list NEWLINE ;
target_dir      : TARGET_KW COLON value_list NEWLINE ;
trace_dir       : TRACE_KW COLON value_list NEWLINE ;
namespace_stmt  : NAMESPACE_KW COLON STRING_LITERAL NEWLINE ;
import_stmt     : IMPORT_KW STRING_LITERAL (AS_KW soft_id)? NEWLINE ;

// ===================================================================
// Decisions
// ===================================================================

decision_blk
    : DECISION_KW STRING_LITERAL annotations? COLON NEWLINE
      INDENT
      CHOSEN_KW COLON STRING_LITERAL NEWLINE
      (RATIONALE_KW COLON STRING_LITERAL NEWLINE)?
      (ALTERNATIVES_KW COLON list_literal NEWLINE)?
      (AFFECTS_KW COLON list_literal NEWLINE)?
      DEDENT
    ;

// ===================================================================
// Types
// ===================================================================

type_def
    : TYPE_KW soft_id annotations? COLON (NEWLINE INDENT (field_def | annotations | NEWLINE)+ DEDENT | field_def | type_expr)
    ;

field_def
    : type_expr COLON type_expr annotations? NEWLINE
    ;

type_expr
    : (soft_id | STRING_LITERAL) (DOT soft_id)* (LANGLE type_expr (COMMA type_expr)* RANGLE)?
    | INTEGER              // Literal integer type, e.g. 42
    | FLOAT_LITERAL        // Literal float type, e.g. 3.14
    | ENUM_KW LPAREN (soft_id | STRING_LITERAL) (COMMA (soft_id | STRING_LITERAL))* RPAREN
    | OPTIONAL_KW LANGLE type_expr RANGLE
    ;

// ===================================================================
// Components
// ===================================================================

component_def
    : COMPONENT_KW soft_id annotations? COLON NEWLINE
      INDENT
      (component_body_item | NEWLINE)+
      DEDENT
    ;

component_body_item
    : PATTERN_KW COLON (STRING_LITERAL | soft_id) NEWLINE
    | DEPENDENCIES_KW COLON list_literal NEWLINE
    | annotations NEWLINE
    | INTERFACE_KW COLON (NEWLINE INDENT (method_sig | field_def | annotations NEWLINE | NEWLINE)+ DEDENT | method_sig)
    | RESOURCES_KW COLON (NEWLINE INDENT (bullet_item | NEWLINE)+ DEDENT | list_literal NEWLINE)
    ;

bullet_item : MINUS value annotations? NEWLINE ;


method_sig
    : soft_id LPAREN param_list? RPAREN ARROW type_expr annotations? NEWLINE
    ;

param_list
    : param (COMMA param)*
    ;

param
    : soft_id (COLON type_expr)? annotations?
    ;

// ===================================================================
// Flows
// ===================================================================

flow_def
    : FLOW_KW soft_id (LPAREN param_list? RPAREN)? (ARROW type_expr)? annotations? COLON NEWLINE
      INDENT
      (flow_step | match_expr | field_def | NEWLINE)+
      DEDENT
    ;

flow_step
    : (STEP_NUM)? (control_flow | action | match_expr) annotations? NEWLINE? (internal_block)?
    | annotations NEWLINE? (internal_block)?
    ;


internal_block
    : INDENT (otherwise_stmt | step_property NEWLINE | flow_step | match_expr | NEWLINE)+ DEDENT
    ;

otherwise_stmt
    : OTHERWISE_KW (THROW_KW | RETURN_KW) expr NEWLINE
    ;

step_property
    : (soft_id COLON | soft_id EQUALS) (expr | value_list) annotations?
    ;

permissive_token
    : soft_id | STRING_LITERAL | BACKTICK | COMMA | LPAREN | RPAREN | SQUOTE | CARET | EQUALS | MINUS | PLUS | ASTERISK | HASH | LANGLE | RANGLE | LBRACKET | RBRACKET | LBRACE | RBRACE | ELLIPSIS | DOT | INTEGER | FLOAT_LITERAL | SLASH | EQ_OP | NE_OP | LE_OP | GE_OP | ARROW | COLON | OR_OP
    ;

action
    : VALIDATE_KW (STRING_LITERAL | expr)? permissive_token* COLON?
    | ACHIEVE_KW STRING_LITERAL (AND_KW STRING_LITERAL)* (COLON | EQUALS)? permissive_token*
    | CREATE_KW (type_expr | soft_id) (COLON | EQUALS)? permissive_token* (COLON permissive_token*)?
    | PERSIST_KW expr (VIA_KW expr)? (COLON | EQUALS)? permissive_token*
    | RETURN_KW (expr | type_expr)? permissive_token*
    | LOG_KW (STRING_LITERAL | expr)? permissive_token*
    | THROW_KW expr? permissive_token*
    | EXECUTE_KW (STRING_LITERAL | expr)? permissive_token*
    | TRANSFORM_KW expr ((VIA_KW | COMMA) expr)? (COLON | EQUALS)? permissive_token*
    | TRANSFORM_KW LPAREN annotation RPAREN
    | UPDATE_KW expr? permissive_token*
    | APPLY_KW STRATEGY_KW soft_id (LPAREN value_list? RPAREN)?
    | soft_id (DOT soft_id)* (LPAREN value_list? RPAREN)? permissive_token* (COLON permissive_token*)?
    ;

control_flow
    : ENSURE_KW expr annotations? (OTHERWISE_KW (THROW_KW | RETURN_KW | soft_id)? expr annotations?)?
    | IF_KW expr COLON (NEWLINE INDENT (flow_step | NEWLINE)+ DEDENT | flow_step | action)
      (NEWLINE? ELSE_KW COLON? (NEWLINE INDENT (flow_step | NEWLINE)+ DEDENT | flow_step | action))?
    | ELSE_KW COLON? (NEWLINE INDENT (flow_step | NEWLINE)+ DEDENT | flow_step | action)
    | ON_ERROR_KW annotations? COLON (NEWLINE INDENT (flow_step | action | NEWLINE)+ DEDENT | flow_step | action)
    ;

match_section
    : match_expr NEWLINE?
    ;

match_expr
    : MATCH_KW (expr | soft_id+) COLON NEWLINE
      INDENT
      (match_case | NEWLINE)+
      DEDENT
    ;

match_case
    : (match_pattern (OR_OP match_pattern)* | DEFAULT_KW) (ARROW | COLON) 
      (NEWLINE INDENT match_case_block_items DEDENT | flow_step | action | expr | NEWLINE)
    ;

match_pattern
    : CONTAINS_KW? (expr | STRING_LITERAL) permissive_token*
    ;

match_case_block_items
    : (flow_step | match_expr | NEWLINE)+
    ;
ensure_stmt
    : ENSURE_KW COLON STRING_LITERAL annotations? NEWLINE
    ;

// ===================================================================
// Strategy
// ===================================================================

strategy_def
    : STRATEGY_KW soft_id annotations? COLON NEWLINE
      INDENT
      (strategy_item | field_def | annotations NEWLINE | NEWLINE)+
      DEDENT
    ;

strategy_item
    : ALGORITHM_KW COLON (STRING_LITERAL | type_expr) annotations? NEWLINE
    | PRECONDITION_KW COLON ((expr | soft_id) (soft_id | STRING_LITERAL)* | type_expr) annotations? NEWLINE
    | INVARIANT_KW COLON (STRING_LITERAL | expr | type_expr) annotations? NEWLINE
    | COMPLEXITY_KW COLON (expr | type_expr) annotations? NEWLINE
    | INPUT_KW COLON (NEWLINE INDENT (param NEWLINE)+ DEDENT | param_list NEWLINE | list_literal NEWLINE | type_expr annotations? NEWLINE)
    | OUTPUT_KW COLON type_expr annotations? NEWLINE
    | SORT_KEY_KW COLON (expr | type_expr) annotations? NEWLINE
    | ORDER_KW COLON soft_id annotations? NEWLINE
    ;

// ===================================================================
// Constraints & Invariants
// ===================================================================

constraint_stmt : CONSTRAINT_KW soft_id? COLON (STRING_LITERAL | value) annotations? NEWLINE ;
invariant_stmt  : INVARIANT_KW soft_id? COLON (STRING_LITERAL | value) annotations? NEWLINE ;

// ===================================================================
// Pattern Matching
// ===================================================================

// (Moved match_expr up)

// ===================================================================
// Human-in-the-Loop
// ===================================================================

question_stmt
    : QUESTION_KW COLON STRING_LITERAL NEWLINE
      INDENT
      (BLOCKING_KW COLON BOOLEAN_LITERAL NEWLINE)?
      (CONTEXT_KW COLON expr NEWLINE)?
      DEDENT
    ;

approve_blk
    : APPROVE_KW STRING_LITERAL COLON NEWLINE
      INDENT
      STATUS_KW COLON (soft_id | STRING_LITERAL) NEWLINE // APPROVED | REJECTED
      BY_KW COLON STRING_LITERAL NEWLINE
      DATE_KW COLON STRING_LITERAL NEWLINE
      (NOTES_KW COLON STRING_LITERAL NEWLINE)?
      DEDENT
    ;

todo_stmt
    : TODO_KW COLON STRING_LITERAL annotations? NEWLINE
    ;

review_stmt
    : REVIEW_KW COLON STRING_LITERAL annotations? NEWLINE
    ;

// ===================================================================
// Expressions & Values
// ===================================================================

value
    : annotation
    | soft_id ARROW expr
    | base_value TO_KW value
    | base_value (DOT (soft_id | INTEGER))+ (LPAREN value_list? RPAREN)? (IS_KW value)?
    | base_value (LPAREN value_list? RPAREN) (IS_KW value)?
    | base_value (IS_KW value)
    | base_value
    ;

value_list
    : (value | named_arg) ( (COMMA)? (value | named_arg))*
    ;

named_arg
    : soft_id (EQUALS | COLON) value
    ;

base_value
    : STRING_LITERAL
    | INTEGER
    | FLOAT_LITERAL
    | BOOLEAN_LITERAL
    | soft_id
    | list_literal
    | map_literal
    ;


list_literal
    : LBRACKET (NEWLINE | INDENT | DEDENT | (value | named_arg) (COMMA (value | named_arg))* (COMMA)? | ASTERISK)* RBRACKET
    ;

map_literal
    : LBRACE (map_entry (COMMA map_entry)*)? RBRACE
    ;

map_entry
    : (STRING_LITERAL | soft_id) COLON expr
    | ELLIPSIS expr
    ;

expr
    : LPAREN expr RPAREN                                                    #ParenExpr
    | NOT_KW expr                                                           #NotExpr
    | left=expr op=(ASTERISK | SLASH) right=expr                            #ArithmeticExpr
    | left=expr op=(PLUS | MINUS) right=expr                               #ArithmeticExpr
    | left=expr (comparison_op | HAS_KW) right=expr                         #ComparisonExpr
    | left=expr (AND_KW | OR_KW) right=expr                                 #LogicalExpr
    | value                                                                 #ValueExpr
    ;
// Riverside
comparison_op
    : EQ_OP | NE_OP | LE_OP | GE_OP | LANGLE | RANGLE | IS_KW | IS_NOT_KW | EQUALS
    ;

// ===================================================================
// Annotations
// ===================================================================

annotations
    : annotation+
    ;

annotation
    : AT soft_id (LPAREN value_list? RPAREN | value_list)?
    ;
// ===================================================================
// Soft Identifier (Allows keywords to be used as IDs in certain contexts)
// ===================================================================

soft_id
    : IDENTIFIER
    | CONTEXT_KW
    | TARGET_KW
    | TRACE_KW
    | NAMESPACE_KW
    | IMPORT_KW
    | AS_KW
    | DECISION_KW
    | CHOSEN_KW
    | RATIONALE_KW
    | ALTERNATIVES_KW
    | AFFECTS_KW
    | TYPE_KW
    | LIST_KW
    | MAP_KW
    | ENUM_KW
    | OPTIONAL_KW
    | COMPONENT_KW
    | INTERFACE_KW
    | PATTERN_KW
    | DEPENDENCIES_KW
    | FLOW_KW
    | VALIDATE_KW
    | ACHIEVE_KW
    | CREATE_KW
    | PERSIST_KW
    | RETURN_KW
    | LOG_KW
    | ENSURE_KW
    | OTHERWISE_KW
    | THROW_KW
    | EXECUTE_KW
    | TRANSFORM_KW
    | ON_ERROR_KW
    | IF_KW
    | ELSE_KW
    | VIA_KW
    | STRATEGY_KW
    | ALGORITHM_KW
    | PRECONDITION_KW
    | COMPLEXITY_KW
    | INPUT_KW
    | OUTPUT_KW
    | SORT_KEY_KW
    | ORDER_KW
    | CONSTRAINT_KW
    | INVARIANT_KW
    | MATCH_KW
    | DEFAULT_KW
    | QUESTION_KW
    | APPROVE_KW
    | STATUS_KW
    | BY_KW
    | DATE_KW
    | NOTES_KW
    | BLOCKING_KW
    | TODO_KW
    | REVIEW_KW
    | IS_KW
    | NOT_KW
    | AND_KW
    | OR_KW
    | UPDATE_KW
    | APPLY_KW
    | CONTAINS_KW
    | HAS_KW
    | TO_KW
    | RESOURCES_KW
    ;
