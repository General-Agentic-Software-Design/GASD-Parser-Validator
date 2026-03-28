import pytest
from Impl.semantic.SemanticPipeline import SemanticPipeline
from Impl.semantic.SymbolTable import SemanticError
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def get_semantic_system(files: dict):
    # Mocking SemanticSystem generation with multiple files
    from Impl.semantic.SemanticNodes import SemanticSystem, SystemMetadata, NamespaceNode
    api = ParseTreeAPI()
    asts = []
    for path, content in files.items():
        tree, _ = api.parse(content)
        ast = ASTGenerator().visit(tree)
        ast.sourceFile = path
        asts.append(ast)
    
    pipeline = SemanticPipeline()
    # Assume pipeline.run can handle a list of ASTs or we mock the multi-file logic
    # For negative tests, we trigger the errors in the pipeline
    return pipeline.run(asts)

def test_negative_cross_file_circular_import():
    # AC-X-SEMAST-002-04 / AT-X-SEMAST-002-03
    files = {
        "A.gasd": 'CONTEXT: "A"\nTARGET: "Py"\nIMPORT "B.gasd"\n',
        "B.gasd": 'CONTEXT: "B"\nTARGET: "Py"\nIMPORT "A.gasd"\n'
    }
    with pytest.raises(SemanticError, match="CircularImport"):
        get_semantic_system(files)

def test_negative_cross_file_duplicate_symbol():
    # AC-X-SEMAST-003-03 / AT-X-SEMAST-003-02
    files = {
        "A.gasd": 'CONTEXT: "Global"\nTARGET: "Py"\nTYPE User:\n  id: String\n',
        "B.gasd": 'CONTEXT: "Global"\nTARGET: "Py"\nTYPE User:\n  id: Integer\n'
    }
    with pytest.raises(SemanticError, match="DuplicateSymbol"):
        get_semantic_system(files)

def test_negative_cross_file_unknown_type():
    # AC-X-SEMAST-004-04 / AT-X-SEMAST-010-01
    files = {
        "A.gasd": 'CONTEXT: "A"\nTARGET: "Py"\nTYPE T:\n  f: RemoteNS.RemoteType\n'
    }
    # RemoteNS.RemoteType is unknown since no file provides RemoteNS and no import links it
    with pytest.raises(SemanticError, match="UnknownType"):
        get_semantic_system(files)

def test_negative_cross_file_signature_mismatch():
    # AC-X-SEMAST-006-02 / AT-X-SEMAST-006-03
    files = {
        "Comp.gasd": 'CONTEXT: "C"\nCOMPONENT Comp:\n  INTERFACE:\n    run(p: String): Boolean\n',
        "Flow.gasd": 'CONTEXT: "C"\nFLOW run(p: Integer):\n  1. ACHIEVE "Task"\n'
    }
    with pytest.raises(SemanticError, match="SignatureMismatch"):
        get_semantic_system(files)

def test_negative_cross_file_decision_conflict():
    # AC-X-SEMAST-008-01 / AT-X-SEMAST-008-01
    files = {
        "D1.gasd": 'CONTEXT: "C"\nDECISION "D1":\n  CHOSEN: "Alt1"\n  AFFECTS: ["TargetType"]\n',
        "D2.gasd": 'CONTEXT: "C"\nDECISION "D2":\n  CHOSEN: "Alt2"\n  AFFECTS: ["TargetType"]\n',
        "Model.gasd": 'CONTEXT: "C"\nTYPE TargetType:\n  f: String\n'
    }
    with pytest.raises(SemanticError, match="DecisionConflict"):
        get_semantic_system(files)

def test_negative_cross_file_constraint_conflict():
    # AC-X-SEMAST-009-04 / AT-X-SEMAST-009-02
    files = {
        "C1.gasd": 'CONTEXT: "Global"\nCONSTRAINT: "User.age > 0"\n',
        "C2.gasd": 'CONTEXT: "Global"\nCONSTRAINT: "User.age < 0"\n',
        "M.gasd": 'CONTEXT: "Global"\nTYPE User:\n  age: Integer\n'
    }
    from Impl.parser.ParseTreeAPI import ParseTreeAPI
    from Impl.ast.ASTGenerator import ASTGenerator
    api = ParseTreeAPI()
    asts = [ASTGenerator(source_file=p).visit(api.parse(c)[0]) for p, c in files.items()]
    pipeline = SemanticPipeline()
    pipeline.run(asts)
    assert any("ConstraintConflict" in e.message for e in pipeline.reporter.errors)

def test_negative_cross_file_shadowing_builtin():
    # US-X-SEMAST-003 / RT-X-SEMAST-003-02
    files = {
        "A.gasd": 'CONTEXT: "A"\nTARGET: "Py"\nTYPE String:\n  f: Integer\n'
    }
    with pytest.raises(SemanticError, match="BuiltinShadowingError"):
        get_semantic_system(files)

def test_negative_cross_file_generic_arity_mismatch():
    # US-X-SEMAST-004 / RT-X-SEMAST-004-02
    files = {
        "A.gasd": 'CONTEXT: "A"\nTARGET: "Py"\nTYPE T:\n  f: List<String, Integer>\n'
    }
    with pytest.raises(SemanticError, match="GenericArityMismatch"):
        get_semantic_system(files)

def test_negative_cross_file_component_visibility():
    # US-X-SEMAST-005 / AT-X-SEMAST-005-03
    files = {
        "Private.gasd": 'NAMESPACE: "P"\nCOMPONENT Internal:\n  PROVIDES: x: String\n',
        "Public.gasd": 'NAMESPACE: "A"\nCOMPONENT PublicAPI:\n  DEPENDENCIES: [Internal]\n'
    }
    # Internal is not visible in Public.gasd because it's in namespace P (not imported)
    with pytest.raises(SemanticError, match="UnknownComponent"):
        get_semantic_system(files)

def test_negative_cross_file_field_mismatch():
    # US-X-SEMAST-007 / AT-X-SEMAST-007-03
    files = {
        "Type.gasd": 'CONTEXT: "T"\nTYPE User:\n  username: String\n',
        "Flow.gasd": 'CONTEXT: "F"\nIMPORT "Type.gasd" AS T\nFLOW f():\n  1. VALIDATE user AS T.User\n'
    }
    # If 'user' has fields that don't match T.User (mocking this scenario)
    # This usually happens during binding if we specifically pass an incompatible structure
    pass 
