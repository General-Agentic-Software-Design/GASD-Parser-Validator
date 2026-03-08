import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_backticks_and_natural_language_actions():
    """RT: Backticks and natural language descriptions in actions parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW backtick_test():
    1. LOG `Checking state`
    2. ACHIEVE "Normalization": e.g., x = y + z
    3. CREATE object: new `Symbol` with @attr
    4. soft_id.call(`arg`)
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"
    
    ast = ASTGenerator().visit(tree)
    assert len(ast.flows[0].steps) == 4

def test_complex_match_and_contains():
    """RT: MATCH with multiple patterns, OR_OP, and CONTAINS prefix parses correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW match_test():
    1. MATCH state:
        CONTAINS "Error" | "Failure" -> LOG "Bad"
        "Success": RETURN OK
        DEFAULT -> THROW `Unknown`
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_shorthand_annotations_and_dotted_labels():
    """RT: Shorthand annotations with dotted labels (e.g. #US-1.1) parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
TYPE User @trace(#REQ-1.1, #REQ-1.2):
    name: String
    
FLOW trace_test() @trace(#US-5.2):
    1. RETURN result @trace(#AC-27.1, #AC-27.2)
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_permissive_return_with_types():
    """RT: RETURN supporting type expressions like List<T>."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW return_type_test():
    1. RETURN List<CompletionItem>
    2. RETURN Map<String, Integer>
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_natural_language_match_expression():
    """RT: MATCH with multiple soft_ids (natural language style)."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW match_nl_test():
    1. MATCH the current user state:
        "ACTIVE" -> RETURN
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_resources_and_bullet_items():
    """RT: RESOURCES section with bullet items (hyphen/minus) parses correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
COMPONENT MyComp:
    RESOURCES:
        - item1
        - item2 @annot
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_multiline_list_with_trailing_comma():
    """RT: Multi-line lists with optional trailing commas parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
COMPONENT MyComp:
    DEPENDENCIES: [
        "Dep1",
        "Dep2",
    ]
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_complex_symbols_in_actions():
    """RT: Actions supporting arithmetic and extra symbols (e.g. ^, +, -, *, /, =)."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
FLOW symbols_test():
    1. ACHIEVE "Calculation": x = (y + z) * 2 / a ^ 2
    2. TRANSFORM data via x + 1
    3. LOG "Result is " + val
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_versioned_identifiers_and_dot_integers():
    """RT: Identifiers with dot-separated integers (e.g. 1.1) parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
FLOW version_test():
    1. RETURN #AC-27.1
    2. LOG SymbolInformation.kind
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_create_with_indented_block():
    """RT: CREATE keyword followed by a colon and indented description block."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
FLOW create_block_test():
    1. CREATE instance:
        This is a complex 
        indented description
    2. RETURN
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.get_errors()}"
