import pytest
from Impl.semantic.SemanticNodes import SemanticNodeBase, ResolvedTypeNode, ResolvedComponentNode, ResolvedFlowNode, SourceRange, NamespaceNode, SemanticSystem, SystemMetadata, TypeContract, ResolvedFieldNode
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticPipeline import SemanticPipeline

def get_semantic_system(files: dict) -> SemanticSystem:
    api = ParseTreeAPI()
    generator = ASTGenerator()
    pipeline = SemanticPipeline()
    
    asts = []
    for path, content in files.items():
        tree, reporter = api.parse(content)
        assert not reporter.has_errors(), f"Parse errors in {path}: {reporter.to_console()}"
        ast = generator.visit(tree)
        ast.sourcePath = path
        asts.append(ast)
        
    return pipeline.run(asts)

def get_semantic_ast(content: str) -> SemanticSystem:
    return get_semantic_system({"global.gasd": content})

def test_semast_core_generation():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem = get_semantic_ast(content)
    assert sem.kind == "SemanticSystem"
    assert hasattr(sem, 'id')

def test_semast_source_maps():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert ns.types["T"].sourceMap is not None
    assert ns.types["T"].sourceMap.startLine == 3

def test_semast_root_system():
    content = 'CONTEXT: "Root"\nTARGET: "Py"\n'
    sem = get_semantic_ast(content)
    assert sem.kind == "SemanticSystem"
    assert "global" in sem.namespaces
    assert sem.metadata.context == "Root"

def test_semast_type_references():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert isinstance(ns.types["T"], ResolvedTypeNode)

def test_semast_flow_analysis():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nFLOW myFlow(x: String) -> Boolean:\n  1. ACHIEVE "Done"\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert "myFlow" in ns.flows
    assert ns.flows["myFlow"].kind == "ResolvedFlow"

def test_semast_component_analysis():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nCOMPONENT C:\n  INTERFACE:\n    run() -> Void\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert "C" in ns.components
    assert isinstance(ns.components["C"], ResolvedComponentNode)

def test_semast_deterministic_hash():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem1 = get_semantic_ast(content)
    sem2 = get_semantic_ast(content)
    assert sem1.hash is not None
    assert sem1.hash == sem2.hash

def test_semast_self_contained():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    import json
    json.dumps(ns.types["T"].to_dict())

def test_semast_flow_step_bindings():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nFLOW fBind(x: String) -> Boolean:\n  1. ACHIEVE "Step1"\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert "fBind" in ns.flows
    assert ns.flows["fBind"].name == "fBind"

def test_semast_model_builder_incremental():
    api = ParseTreeAPI()
    gen = ASTGenerator()
    pipeline = SemanticPipeline()
    
    tree1, _ = api.parse('CONTEXT: "I"\nTARGET: "P"\nTYPE T1:\n  a: String\n')
    tree2, _ = api.parse('CONTEXT: "I"\nTARGET: "P"\nTYPE T2:\n  b: Integer\n')
    ast1 = gen.visit(tree1)
    ast2 = gen.visit(tree2)
    sem = pipeline.run([ast1, ast2])
    ns = sem.namespaces["global"]
    assert "T1" in ns.types
    assert "T2" in ns.types

def test_semast_model_regression_cycles():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE Node:\n  child: Node\n'
    sem = get_semantic_ast(content)
    ns = sem.namespaces["global"]
    assert "Node" in ns.types
    assert "child" in ns.types["Node"].fields

def test_semast_model_regression_empty():
    sem = get_semantic_ast('')
    assert sem.kind == "SemanticSystem"
    ns = sem.namespaces["global"]
    # 18 built-in types (v1.2 adds Date, Int32)
    assert len(ns.types) == 18
    assert len(ns.components) == 0

# ===================================================================
# Cross-File Regression Tests
# ===================================================================

def test_semast_model_regression_path_normalization():
    # RT-X-SEMAST-001-01 (similar)
    files = {
        "./a.gasd": 'CONTEXT: "A"\nTARGET: "Py"\n',
        "b.gasd": 'CONTEXT: "B"\nTARGET: "Py"\n'
    }
    sem = get_semantic_system(files)
    # Normalized paths should be used as keys or in metadata
    assert len(sem.metadata.files) == 2

def test_semast_model_regression_deterministic_order():
    # RT-X-SEMAST-001-02 (similar)
    f1 = {"a.gasd": 'CONTEXT: "A"\n', "b.gasd": 'CONTEXT: "B"\n'}
    f2 = {"b.gasd": 'CONTEXT: "B"\n', "a.gasd": 'CONTEXT: "A"\n'}
    
    sem1 = get_semantic_system(f1)
    sem2 = get_semantic_system(f2)
    
    # Internal order of files in metadata should be sorted
    assert [f.path for f in sem1.metadata.files] == [f.path for f in sem2.metadata.files]
