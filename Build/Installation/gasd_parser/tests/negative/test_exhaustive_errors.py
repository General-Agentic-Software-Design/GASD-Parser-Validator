import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

"""
Exhaustive Negative Test Suite
Covers all V001-V012 semantic errors and S001-S002 syntax errors.
"""

@pytest.fixture
def api():
    return ParseTreeAPI()

@pytest.fixture
def pipeline():
    return ValidationPipeline()

def test_v001_duplicate_names(api, pipeline):
    content = 'CONTEXT: "D"\nTARGET: "P"\nTYPE T: f: S\nTYPE T: f: S\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V011" or e.code == "V001" for e in errors) # ReferenceResolution or Duplicate
    assert any(e.code == "V001" for e in errors)

def test_v002_missing_context(api, pipeline):
    content = 'TARGET: "P"\nTYPE T: f: S\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V002" for e in errors)

def test_v003_missing_target(api, pipeline):
    content = 'CONTEXT: "C"\nTYPE T: f: S\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V003" for e in errors)

def test_v004_empty_file(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V004" for e in errors)

def test_v006_decision_missing_chosen(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nDECISION D:\n    ALTERNATIVES: "A"\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V006" for e in errors)

def test_v007_flow_missing_steps(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nFLOW F():\n    \n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V007" for e in errors)

def test_v008_unknown_type_warning(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nTYPE T: f: Unknown\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V008" and e.severity == "WARNING" for e in errors)

def test_v009_unknown_dependency_warning(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nCOMPONENT C:\n    DEPENDENCIES: UnknownComp\n    INTERFACE: m()\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V009" and e.severity == "WARNING" for e in errors)

def test_v010_decision_affects_unknown(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nDECISION "D":\n    CHOSEN: "A"\n    ALTERNATIVES: ["A"]\n    AFFECTS: ["UnknownThing"]\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V010" and e.severity == "WARNING" for e in errors)

def test_v005_component_missing_methods(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nCOMPONENT C: INTERFACE:\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V005" for e in errors)

def test_v013_strategy_missing_algorithm(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nSTRATEGY S(i: I) -> O:\n' # No algorithm
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V013" for e in errors)

def test_v014_decision_missing_alternatives(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nDECISION D: CHOSEN: "A"\n' # No alternatives
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V014" for e in errors)

def test_strategy_type_resolution(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nSTRATEGY S:\n    INPUT: i: UnknownIn\n    OUTPUT: UnknownOut\n    ALGORITHM: "..."\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V008" and "UnknownIn" in e.message for e in errors)
    assert any(e.code == "V008" and "UnknownOut" in e.message for e in errors)

def test_v011_validate_unknown_type(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE user AS TYPE.Unknown\n'
    tree, _ = api.parse(content)
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    assert any(e.code == "V011" for e in errors)

def test_v012_validate_missing_binding(api, pipeline):
    content = 'CONTEXT: "C"\nTARGET: "P"\nFLOW F():\n    1. VALIDATE user\n'
    tree, _ = api.parse(content)
    # If it parses (fallback to general action), generator might still pick it up
    ast = ASTGenerator().visit(tree)
    errors = pipeline.validate(ast)
    # It might be caught by syntax error first or V012 if it bypasses syntax
    results = api.getErrors() + errors
    assert any("VALIDATE" in str(e) or getattr(e, 'code', '') == "V012" for e in results)

def test_s001_indentation_error(api):
    content = 'CONTEXT: "C"\nTARGET: "P"\nTYPE T:\n  f: S\n    wrong: I\n'
    _, reporter = api.parse(content)
    assert reporter.get_error_count() > 0

def test_s002_syntax_missing_colon(api):
    content = 'CONTEXT: "C"\nTARGET: "P"\nTYPE T\n  f: S\n'
    _, reporter = api.parse(content)
    assert reporter.get_error_count() > 0
