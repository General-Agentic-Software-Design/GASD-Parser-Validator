import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def parse_snippet(source: str):
    api = ParseTreeAPI()
    tree, reporter = api.parse(source)
    return tree, reporter

class TestParserRegressionFixes:
    """
    Comprehensive regression tests to cover parser bugs found and fixed 
    during the validation of the 36 Reference Specifications.
    """

    def test_line_comment_does_not_consume_identifiers(self):
        # Bug: `LINE_COMMENT` rule bare 'GASD' consumed identifiers like 'GASDVisitor'
        # Bug: Bare '#' consumed '#US-001'
        source = '''CONTEXT: "Test"
TARGET: "Test"

COMPONENT TestComponent @trace #US-001:
    DEPENDENCIES: [GASDVisitor, GASDParser]
    INTERFACE:
        test() -> Void
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"
        
        # Verify component and dependencies are correctly parsed
        assert tree is not None

    def test_top_level_annotations_before_newlines(self):
        # Bug: Standalone annotations before a NEWLINE caused cascading parse failures
        source = '''CONTEXT: "Test"
TARGET: "Test"

@authorized("all")
@agent_note("Important notice")

COMPONENT UIComponent:
    INTERFACE:
        render(items: List<Entry>) -> Void
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_doc_comments_inside_indented_blocks(self):
        # Bug: GASDIndentationLexer suppressed INDENT on `///` lines, breaking blocks
        source = '''CONTEXT: "Test"
TARGET: "Test"

COMPONENT APIComponent:
    INTERFACE:
        /// Parses the input string
        parse(source: String) -> Void
        /// Validates the structure
        validate() -> Boolean
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_permissive_tokens_with_complex_actions(self):
        # Bug: ACHIEVE and MATCH statements failed on relational operators and arrows
        source = '''CONTEXT: "Test"
TARGET: "Test"

FLOW math_flow():
    1. ACHIEVE "Evaluation" (sin(PI/2)*5 + sqrt(25) == 10)
    2. ACHIEVE "Roots" (x^2 - 5x + 6 = 0 -> Roots: 3, 2)
    3. MATCH state:
        "DIGIT" | "OPERATOR": ACHIEVE "Append"
        "ACTION" (e.g. "Plot"): ACHIEVE "Trigger"
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_list_literal_in_strategy_input(self):
        # Bug: `INPUT` directive in `STRATEGY` couldn't accept single-line lists
        source = '''CONTEXT: "Test"
TARGET: "Test"

STRATEGY PlotResolution:
    ALGORITHM: "Adaptive"
    INPUT: [fn: String, view: ViewPort, res: Integer]
    OUTPUT: "Array of Points"
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_informal_headers_handled_gracefully(self):
        # Bug: `*/` and `GASD Design:` without indent caused parsing failures
        source = '''// GASD Design: Application Flows v1.0.0
// ==============================
// Scope: Evaluation Flow
*/
CONTEXT: "Test"
TARGET: "Test"

FLOW simple_flow():
    1. RETURN "Done"
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_enum_and_optional_in_annotation_args(self):
        # Bug: ENUM_KW and OPTIONAL_KW were missing from soft_id, breaking annotation args
        # Bug: generic types (Optional<T>, List<T>) were not allowed as values in annotations
        # Bug: @transaction_type was missing its 't' argument in the registry
        # Bug: @async was not allowed in TYPE scope (needed for GASD metamodel)
        source = '''CONTEXT: "Test"
TARGET: "Test"

TYPE T:
    @transaction_type(t: Enum("SAGA", "ACID", "BASE"))
    @status(s: Enum("DRAFT", "APPROVED"))
    @rest(verb: Enum("GET", "POST"), path: String)
    @config(opt: Optional<String>)
    @meta(type: List<String>)
    @async
    field: String
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"

    def test_async_in_type_scope_metamodel(self):
        # Bug: Annotation @async is not allowed in scope TYPE
        # This is needed for the authoritative gasd-1.2.0.gasd file
        source = '''CONTEXT: "Test"
TARGET: "Test"

TYPE StandardAnnotation:
    @async
    @transaction_type(t: Enum("SAGA", "ACID"))
'''
        tree, reporter = parse_snippet(source)
        assert not reporter.has_errors(), f"Errors: {reporter.syntax_errors}"
