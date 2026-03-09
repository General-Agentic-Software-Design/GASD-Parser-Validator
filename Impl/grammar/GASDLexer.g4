lexer grammar GASDLexer;

@header {
}

/* 
 * GASD 1.1 Lexer
 * Handles Python-style indentation by omitting INDENT and DEDENT tokens.
 */

// ===================================================================
// Comments & Headers (MAX PRECEDENCE)
// ===================================================================

// NOTE: Informal header patterns require leading whitespace to avoid false matches
//       '#' requires trailing space to preserve #trace-id tokens
LINE_COMMENT   : ('//' | '# ' | [ \t]* '*/' | [ \t]+ ('GASD ' | '===' | 'Scope:' | 'Compliance:' | 'Output:' | 'Status:' | 'Version:')) ~[\r\n]* -> skip ;
BLOCK_COMMENT  : '/*' .*? '*/' -> skip ;
MARKDOWN_FENCE : '```' ~[\r\n]* -> skip ;
DOC_COMMENT    : '///' ~[\r\n]* -> channel(HIDDEN) ;

// ===================================================================
// Keywords (Case-Sensitive, UPPERCASE)
// ===================================================================

CONTEXT_KW     : 'CONTEXT' ;
TARGET_KW      : 'TARGET' ;
TRACE_KW       : 'TRACE' ;
NAMESPACE_KW   : 'NAMESPACE' ;
IMPORT_KW      : 'IMPORT' ;
AS_KW          : 'AS' ;

DECISION_KW    : 'DECISION' ;
CHOSEN_KW      : 'CHOSEN' ;
RATIONALE_KW   : 'RATIONALE' ;
ALTERNATIVES_KW: 'ALTERNATIVES' ;
AFFECTS_KW     : 'AFFECTS' ;

TYPE_KW        : 'TYPE' ;
LIST_KW        : 'List' ;
MAP_KW         : 'Map' ;
ENUM_KW        : 'Enum' ;
OPTIONAL_KW    : 'Optional' ;

COMPONENT_KW   : 'COMPONENT' ;
INTERFACE_KW   : 'INTERFACE' ;
PATTERN_KW     : 'PATTERN' ;
DEPENDENCIES_KW: 'DEPENDENCIES' ;

FLOW_KW        : 'FLOW' ;
VALIDATE_KW    : 'VALIDATE' ;
ACHIEVE_KW     : 'ACHIEVE' ;
CREATE_KW      : 'CREATE' ;
PERSIST_KW     : 'PERSIST' ;
RETURN_KW      : 'RETURN' ;
LOG_KW         : 'LOG' ;
ENSURE_KW      : 'ENSURE' ;
OTHERWISE_KW   : 'OTHERWISE' ;
THROW_KW       : 'THROW' ;
EXECUTE_KW     : 'EXECUTE' ;
TRANSFORM_KW   : 'TRANSFORM' ;
UPDATE_KW      : 'UPDATE' ;
APPLY_KW       : 'APPLY' ;
WITH_KW        : 'WITH' ;
ON_ERROR_KW    : 'ON_ERROR' ;
IF_KW          : 'IF' ;
ELSE_KW        : 'ELSE' ;
VIA_KW         : 'via' ;
CONTAINS_KW    : 'CONTAINS' ;
HAS_KW         : 'HAS' ;
TO_KW          : 'to' ;
RESOURCES_KW   : 'RESOURCES' ;

STRATEGY_KW    : 'STRATEGY' ;
ALGORITHM_KW   : 'ALGORITHM' ;
PRECONDITION_KW: 'PRECONDITION' ;
COMPLEXITY_KW  : 'COMPLEXITY' ;
INPUT_KW       : 'INPUT' ;
OUTPUT_KW      : 'OUTPUT' ;
SORT_KEY_KW    : 'SORT_KEY' ;
ORDER_KW       : 'ORDER' ;
IS_NOT_KW      : 'IS NOT' ;
IS_KW          : 'IS' ;
NOT_KW         : 'NOT' ;
AND_KW         : 'AND' ;
OR_KW          : 'OR' ;

CONSTRAINT_KW  : 'CONSTRAINT' ;
INVARIANT_KW   : 'INVARIANT' ;

MATCH_KW       : 'MATCH' ;
DEFAULT_KW     : 'DEFAULT' ;

QUESTION_KW    : 'QUESTION' ;
APPROVE_KW     : 'APPROVE' ;
STATUS_KW      : 'STATUS' ;
BY_KW          : 'BY' ;
DATE_KW        : 'DATE' ;
NOTES_KW       : 'NOTES' ;
BLOCKING_KW    : 'BLOCKING' ;
TODO_KW        : 'TODO' ;
REVIEW_KW      : 'REVIEW' ;

// ===================================================================
// Symbols & Operators
// ===================================================================

COLON    : ':' ;
BACKTICK : '`' ;
COMMA    : ',' ;
DOT      : '.' ;
ARROW    : '->' ;
LPAREN   : '(' ;
RPAREN   : ')' ;
LBRACKET : '[' ;
RBRACKET : ']' ;
LANGLE   : '<' ;
RANGLE   : '>' ;
EQUALS   : '=' ;
LBRACE   : '{' ;
RBRACE   : '}' ;
ELLIPSIS : '...' ;
AT       : '@' ;
CARET    : '^' ;
SQUOTE   : '\'' ;
ASTERISK : '*' ;
PLUS     : '+' ;
MINUS    : '-' ;
SLASH    : '/' ;
EQ_OP    : '==' ;
NE_OP    : '!=' ;
LE_OP    : '<=' ;
GE_OP    : '>=' ;

// ===================================================================
// Literals & Identifiers
// ===================================================================

STEP_NUM : INTEGER DOT ;
BOOLEAN_LITERAL : 'true' | 'false' | 'TRUE' | 'FALSE' ;
INTEGER : '-'? [0-9]+ ;
FLOAT_LITERAL : '-'? [0-9]+ '.' [0-9]+ ;
STRING_LITERAL : '"' (~["\\] | '\\' .)* '"' ;

IDENTIFIER : [#a-zA-Z_] [#a-zA-Z0-9_-]* ;
OR_OP      : '|' ;

// ===================================================================
// Indentation & Whitespace
// ===================================================================

// We define synthetic tokens here for the parser to use.
// A real Python-style lexer in Python will subclass this lexer
// and emit these tokens programmatically based on leading spaces.
INDENT : '<INDENT>' ;
DEDENT : '<DEDENT>' ;
NEWLINE : ('\r'? '\n')+ ;

// Normal space/tabs (not at start of line) are ignored.
WS : [ \t]+ -> skip ;

// ===================================================================
// Lowest Precedence
// ===================================================================

HASH     : '#' ;
