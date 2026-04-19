import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator

def test_arithmetic_and_logic_expressions():
    """RT: Arithmetic and logical operators are parsed correctly without syntax errors."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW calc():
    1. MATCH code:
        "VIP" -> RETURN price * 0.8
        "FLAT" -> RETURN price - 10
        DEFAULT -> RETURN price + 5 / 2
    2. IF stock < 10 AND valid == TRUE:
        RETURN
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"
    
    ast = generator = ASTGenerator().visit(tree)
    # Just checking it doesn't crash AST generation
    assert len(ast.flows) == 1

def test_lambda_and_annotation_expressions():
    """RT: Lambda arrows in values and annotations in expressions (e.g. TRANSFORM) parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW exec():
    1. IF list.contains(x -> x.val < 0.5):
        TRANSFORM(@generate("UUID"))
    2. ACHIEVE "Filter":
        input: filter(y -> y.active == TRUE)
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_flexible_precondition_and_apply():
    """RT: Flexible PRECONDITION (multiple soft_ids/strings) and APPLY keywords parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"

STRATEGY search:
    ALGORITHM: "Binary"
    PRECONDITION: input IS_SORTED "Requires sorted list"
    COMPLEXITY: O(log n)
    INPUT:
        target: Integer
    OUTPUT: Integer

FLOW run():
    APPLY STRATEGY search(target)
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_standalone_annotations():
    """RT: Standalone annotations in FLOW blocks parse correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW annotated_flow():
    @error_strategy("Fail-Fast")
    1. VALIDATE input AS TYPE.Input
    @trace("REQ-1")
    2. RETURN output
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.to_console()}"

def test_otherwise_in_control_flow():
    """RT: OTHERWISE as standalone action or within ENSURE parses correctly."""
    api = ParseTreeAPI()
    content = """
CONTEXT: "Test"
TARGET: "TypeScript"
FLOW ensure_otherwise():
    1. ENSURE valid
        OTHERWISE RETURN error
    2. IF check:
        RETURN OK
    3. ELSE:
        LOG "failed" 
        RETURN error
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0, f"Expected 0 errors, got {errors.get_errors()}"
