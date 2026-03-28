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
    | contract_def
    | model_def
    | assumption_def
    | ensure_stmt
    | match_section
    | question_stmt
    | approve_blk
    | todo_stmt
    | review_stmt
    | annotations NEWLINE
    // Skip extra newlines between sections
    | NEWLINE
    | version_dir
    ;

// ===================================================================
// Directives
// ===================================================================

version_dir     : VERSION_KW COLON? (version_number | STRING_LITERAL) NEWLINE ;
version_number  : FLOAT_LITERAL | (INTEGER DOT INTEGER (DOT INTEGER)?) ;
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
    : TYPE_KW soft_id annotations? COLON (NEWLINE INDENT (type_body_item | NEWLINE)+ DEDENT | field_def | type_expr)
    ;

type_body_item
    : field_def
    | annotations NEWLINE
    ;

field_def
    : soft_id COLON type_expr (AS_KW alias_val)? (annotations? NEWLINE | NEWLINE INDENT (annotation | NEWLINE)+ DEDENT)
    ;

type_expr
    : (soft_id | STRING_LITERAL) (DOT soft_id)* LANGLE type_expr (COMMA type_expr)* RANGLE      #GenericType
    | LBRACE param_list? RBRACE                                                               #RecordType
    | ENUM_KW LPAREN (soft_id | STRING_LITERAL) (COMMA (soft_id | STRING_LITERAL))* RPAREN      #EnumType
    | OPTIONAL_KW LANGLE type_expr RANGLE                                                      #OptionalType
    | (soft_id | STRING_LITERAL) (DOT soft_id)*                                                #SimpleType
    | INTEGER                                                                                  #IntType
    | FLOAT_LITERAL                                                                            #FloatType
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
    : step_id (control_flow | action | match_expr)? depends_clause? annotations? NEWLINE? internal_block?
    | (control_flow | action | match_expr) depends_clause? annotations? NEWLINE? internal_block?
    | annotations NEWLINE? internal_block?
    ;

step_id
    : STEP_NUM
    | soft_id DOT
    | (STEP_KW)? (soft_id | INTEGER) COLON
    ;

depends_clause
    : DEPENDS_ON_KW step_ref (COMMA step_ref)*
    ;

depends_stmt
    : depends_clause NEWLINE
    ;
    
step_ref
    : STEP_KW (STEP_NUM | INTEGER | STRING_LITERAL | soft_id)
    ;


internal_block
    : INDENT (depends_stmt | postcondition_stmt | on_error_clause | timeout_stmt | otherwise_stmt | step_property NEWLINE | flow_step | match_expr | NEWLINE)+ DEDENT
    ;

otherwise_stmt
    : OTHERWISE_KW (THROW_KW | RETURN_KW) expr NEWLINE
    ;

postcondition_stmt
    : POSTCONDITION_KW COLON (NEWLINE INDENT (postcondition_expr NEWLINE)+ DEDENT | postcondition_expr NEWLINE)
    ;

postcondition_expr
    : expr
    ;

timeout_stmt
    : TIMEOUT_KW COLON duration_literal NEWLINE
    ;

duration_literal
    : INTEGER (MS_UNIT | S_UNIT | M_UNIT)
    ;

on_error_clause
    : ON_ERROR_KW COLON action
    ;

step_property
    : (soft_id COLON | soft_id EQUALS) (expr | value_list) annotations?
    ;

permissive_token
    : soft_id | STRING_LITERAL | BACKTICK | COMMA | LPAREN | RPAREN | SQUOTE | CARET | EQUALS | MINUS | PLUS | ASTERISK | HASH | LANGLE | RANGLE | LBRACKET | RBRACKET | LBRACE | RBRACE | ELLIPSIS | DOT | INTEGER | FLOAT_LITERAL | SLASH | EQ_OP | NE_OP | LE_OP | GE_OP | ARROW | COLON | OR_OP | AND_KW | OR_KW | NOT_KW | IS_KW | IS_NOT_KW | TO_KW | VIA_KW
    | GLOBAL_KW | LOCAL_KW
    ;

action
    : VALIDATE_KW expr AS_KW TYPE_KW DOT type_expr
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
    | action_id (DOT soft_id)* (LPAREN value_list? RPAREN)? permissive_token* (COLON permissive_token*)?
    ;

action_id
    : IDENTIFIER
    | ACHIEVE_KW
    | CREATE_KW
    | PERSIST_KW
    | RETURN_KW
    | LOG_KW
    | THROW_KW
    | EXECUTE_KW
    | TRANSFORM_KW
    | UPDATE_KW
    | APPLY_KW
    | TYPE_KW
    | RESOURCES_KW
    | CONTEXT_KW
    | TARGET_KW
    | TRACE_KW
    | NAMESPACE_KW
    | IMPORT_KW
    | AS_KW
    | WITH_KW
    | VIA_KW
    | TO_KW
    | HAS_KW
    | CONTAINS_KW
    | IS_KW
    | NOT_KW
    | AND_KW
    | OR_KW
    | MATCH_KW
    | DEFAULT_KW
    | STATUS_KW
    ;

control_flow
    : ENSURE_KW (expr | soft_id)+ annotations? (OTHERWISE_KW (THROW_KW | RETURN_KW | soft_id)? (expr | soft_id)+ annotations?)?
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

constraint_stmt : CONSTRAINT_KW (soft_id | STRING_LITERAL)? COLON (STRING_LITERAL | expr) annotations? NEWLINE ;
invariant_stmt  : (GLOBAL_KW | LOCAL_KW)? INVARIANT_KW (soft_id | STRING_LITERAL)? COLON (STRING_LITERAL | expr) annotations? NEWLINE 
                | INVARIANT_KW (GLOBAL_KW | LOCAL_KW) (soft_id | STRING_LITERAL)? COLON (STRING_LITERAL | expr) annotations? NEWLINE
                ;

// --- GASD 1.2 NEW BLOCKS ---

contract_def
    : CONTRACT_KW (qualified_name | STRING_LITERAL) annotations? COLON NEWLINE
      INDENT
      (input_blk)?
      (output_blk)?
      (BEHAVIORS_KW COLON NEWLINE INDENT (case_blk)+ DEDENT)?
      (case_blk)*
      (idempotent_blk)?
      (version_dir)?
      DEDENT
    ;

input_blk : INPUT_KW COLON (NEWLINE INDENT (param NEWLINE)+ DEDENT | param_list NEWLINE) ;
output_blk : OUTPUT_KW COLON type_expr NEWLINE ;
idempotent_blk : IDEMPOTENT_KW COLON BOOLEAN_LITERAL NEWLINE ;

case_blk
    : CASE_KW (soft_id | STRING_LITERAL) COLON NEWLINE
      INDENT
      (case_clause NEWLINE | flow_step | action NEWLINE | ensure_stmt NEWLINE | NEWLINE)+
      DEDENT
    ;

case_clause
    : POSTCONDITION_KW COLON postcondition_expr
    | THROWS_KW COLON soft_id
    | AFTER_KW COLON (duration_literal | soft_id (LPAREN value_list RPAREN)?)
    ;

model_def
    : MODEL_KW STRING_LITERAL annotations? COLON NEWLINE
      INDENT
      TYPE_KW COLON tech_id NEWLINE
      FILE_KW COLON STRING_LITERAL NEWLINE
      (VERIFIES_KW COLON NEWLINE INDENT (invariant_ref NEWLINE)+ DEDENT)?
      (ASSUMPTIONS_KW COLON NEWLINE INDENT (STRING_LITERAL NEWLINE)+ DEDENT)?
      DEDENT
    ;

invariant_ref : (GLOBAL_KW | LOCAL_KW)? INVARIANT_KW COLON STRING_LITERAL 
              | INVARIANT_KW (GLOBAL_KW | LOCAL_KW) COLON STRING_LITERAL
              ;

assumption_def
    : ASSUMPTION_KW (STRING_LITERAL | soft_id) annotations? COLON NEWLINE
      INDENT
      (AFFECTS_KW COLON list_literal NEWLINE)?
      (CONSEQUENCE_KW COLON STRING_LITERAL NEWLINE)?
      DEDENT
    | ASSUMPTION_KW (STRING_LITERAL | soft_id) annotations? NEWLINE
    | ASSUMPTION_KW COLON STRING_LITERAL NEWLINE
    ;

qualified_name : soft_id (DOT soft_id)* ;

tech_id : (soft_id | PLUS | ASTERISK | HASH | DOT | MINUS)+ ;

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
    : primary_expr
    | value DOT (soft_id | INTEGER)
    | value LPAREN value_list? RPAREN
    | value IS_KW value
    | value TO_KW value
    | value ARROW expr
    | soft_id LANGLE type_expr (COMMA type_expr)* RANGLE
    ;

primary_expr
    : annotation
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
    : AT name=soft_id (LPAREN args=value_list? RPAREN | param_id=param_val (COMMA param_val)*)? (AS_KW alias=alias_val)?
    ;

param_val : IDENTIFIER | STRING_LITERAL ;
alias_val : soft_id | STRING_LITERAL ;
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
    | DECISION_KW
    | CHOSEN_KW
    | RATIONALE_KW
    | ALTERNATIVES_KW
    | AFFECTS_KW
    | LIST_KW
    | MAP_KW
    | ENUM_KW
    | OPTIONAL_KW
    | COMPONENT_KW
    | INTERFACE_KW
    | PATTERN_KW
    | DEPENDENCIES_KW
    | FLOW_KW
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
    | VALIDATE_KW
    | TYPE_KW
    | AS_KW
    | WITH_KW
    | TO_KW
    | HAS_KW
    | CONTAINS_KW
    | APPLY_KW
    | UPDATE_KW
    | RESOURCES_KW
    | IS_KW
    | NOT_KW
    | AND_KW
    | OR_KW
    | VERSION_KW
    | CONTRACT_KW
    | CASE_KW
    | THROWS_KW
    | AFTER_KW
    | LOCAL_KW
    | GLOBAL_KW
    | MODEL_KW
    | FILE_KW
    | VERIFIES_KW
    | ASSUMPTIONS_KW
    | ASSUMPTION_KW
    | CONSEQUENCE_KW
    | IDEMPOTENT_KW
    | TIMEOUT_KW
    | SET_KW
    | DELETE_KW
    | DEPENDS_ON_KW
    | STEP_KW
    | POSTCONDITION_KW
    | BEHAVIORS_KW
    | MS_UNIT
    | S_UNIT
    | M_UNIT
    ;
