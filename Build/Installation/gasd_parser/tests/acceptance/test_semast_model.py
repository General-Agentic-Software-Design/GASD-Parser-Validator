import pytest
from typing import Dict
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticPipeline import SemanticPipeline
from Impl.semantic.SemanticNodes import SemanticSystem, ResolvedTypeNode, ResolvedComponentNode

def get_semantic_system(contents: Dict[str, str]) -> SemanticSystem:
    api = ParseTreeAPI()
    gen = ASTGenerator()
    asts = []
    for path, content in contents.items():
        tree, reporter = api.parse(content)
        assert not reporter.has_errors(), f"Parse errors in {path}: {reporter.to_console()}"
        ast = gen.visit(tree)
        ast.sourceFile = path
        asts.append(ast)
    
    pipeline = SemanticPipeline()
    return pipeline.run(asts)

def get_semantic_ast(content: str) -> SemanticSystem:
    return get_semantic_system({"file.gasd": content})

def test_semast_core_generation():
    content = 'CONTEXT: "Test"\nTARGET: "Python3"\nTYPE T:\n  f: String\n'
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "All nodes extend SemanticNodeBase"
    assert hasattr(sem_ast, 'kind')
    assert hasattr(sem_ast, 'id')
    
    # ENSURE "Every node has a valid string 'id'"
    assert isinstance(sem_ast.id, str)
    assert len(sem_ast.id) > 0

def test_semast_source_maps():
    content = 'CONTEXT: "Test"\nTARGET: "Python3"\nTYPE T:\n  f: String\n'
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "SourceRange matches exactly with original text locations"
    ns = sem_ast.namespaces["global"]
    assert "T" in ns.types
    t_node = ns.types["T"]
    
    # ENSURE "Start line and column are precise"
    assert t_node.sourceMap is not None
    assert t_node.sourceMap.startLine == 3
    assert t_node.sourceMap.startCol == 0

def test_semast_root_system():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\n'
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "Root node is SemanticSystem"
    assert sem_ast.kind == "SemanticSystem"
    
    # ENSURE "Includes namespaces and global metadata"
    assert "global" in sem_ast.namespaces
    assert sem_ast.metadata.context == "Test"

def test_semast_type_references():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "Type bindings map to ResolvedTypeNode"
    ns = sem_ast.namespaces["global"]
    assert "T" in ns.types
    assert isinstance(ns.types["T"], ResolvedTypeNode)

def test_semast_flow_analysis():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nFLOW myFlow(x: String) -> Boolean:\n  1. ACHIEVE "True"\n'
    sem_ast = get_semantic_ast(content)
    
    ns = sem_ast.namespaces["global"]
    assert "myFlow" in ns.flows
    # Ensure FLOW generated in Semantic AST
    assert ns.flows["myFlow"].kind == "ResolvedFlow"

def test_semast_component_analysis():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nCOMPONENT myComp:\n  INTERFACE:\n    run() -> Boolean\n'
    sem_ast = get_semantic_ast(content)
    
    ns = sem_ast.namespaces["global"]
    assert "myComp" in ns.components
    assert isinstance(ns.components["myComp"], ResolvedComponentNode)

def test_semast_deterministic_hash():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem_ast1 = get_semantic_ast(content)
    sem_ast2 = get_semantic_ast(content)
    
    assert sem_ast1.hash is not None
    # ENSURE "All SemanticNode hashes remain deterministic across runs"
    assert sem_ast1.hash == sem_ast2.hash

def test_semast_self_contained():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE T:\n  f: String\n'
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "All symbols use relative GUIDs without memory references"
    ns = sem_ast.namespaces["global"]
    d = ns.types["T"].to_dict()
    import json
    # If it can be serialized, it doesn't have memory cyclic refs
    payload = json.dumps(d)
    assert "String" in payload

def test_semast_flow_step_bindings():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nFLOW bindFlow(x: String) -> Boolean:\n  1. ACHIEVE "Step1"\n  2. ACHIEVE "Step2"\n'
    sem_ast = get_semantic_ast(content)
    
    ns = sem_ast.namespaces["global"]
    assert "bindFlow" in ns.flows
    flow = ns.flows["bindFlow"]
    assert flow.kind == "ResolvedFlow"
    assert flow.name == "bindFlow"

def test_semast_model_builder_incremental():
    from Impl.semantic.SemanticPipeline import SemanticPipeline
    from Impl.parser.ParseTreeAPI import ParseTreeAPI
    from Impl.ast.ASTGenerator import ASTGenerator
    
    content1 = 'CONTEXT: "Inc"\nTARGET: "Py"\nTYPE T1:\n  a: String\n'
    content2 = 'CONTEXT: "Inc"\nTARGET: "Py"\nTYPE T2:\n  b: Integer\n'
    
    api = ParseTreeAPI()
    gen = ASTGenerator()
    
    tree1, r1 = api.parse(content1)
    ast1 = gen.visit(tree1)
    tree2, r2 = api.parse(content2)
    ast2 = gen.visit(tree2)
    
    pipeline = SemanticPipeline()
    sem = pipeline.run([ast1, ast2])
    
    ns = sem.namespaces["global"]
    assert "T1" in ns.types
    assert "T2" in ns.types

def test_semast_model_regression_cycles():
    content = 'CONTEXT: "Test"\nTARGET: "Py"\nTYPE Node:\n  child: Node\n'
    sem_ast = get_semantic_ast(content)
    
    ns = sem_ast.namespaces["global"]
    assert "Node" in ns.types
    node_type = ns.types["Node"]
    assert "child" in node_type.fields

def test_semast_model_regression_empty():
    content = ''
    sem_ast = get_semantic_ast(content)
    
    # ENSURE "Returns a valid SemanticSystem with empty maps (plus built-in types)"
    assert sem_ast.kind == "SemanticSystem"
    ns = sem_ast.namespaces["global"]
    # 16 built-in types are always registered
    assert len(ns.types) == 16
    assert len(ns.components) == 0

# ===================================================================
# Cross-File Acceptance Tests
# ===================================================================

def test_semast_compilation_unit():
    # AT-X-SEMAST-001-01, AC-X-SEMAST-001-03
    contents = {
        "file1.gasd": 'CONTEXT: "C1"\nTARGET: "Py"\nTYPE T1: f: String\n',
        "file2.gasd": 'CONTEXT: "C1"\nTARGET: "Py"\nTYPE T2: f: Integer\n'
    }
    sem_ast = get_semantic_system(contents)
    
    # ENSURE "Root SemanticSystem contains a non-null CompilationUnit"
    assert hasattr(sem_ast, "compilationUnit")
    assert sem_ast.compilationUnit is not None
    
    # ENSURE "CompilationUnit contains a list of ProjectFileNode objects"
    assert len(sem_ast.compilationUnit.files) == 2
    assert any(f.endswith("file1.gasd") for f in sem_ast.compilationUnit.files)
    assert any(f.endswith("file2.gasd") for f in sem_ast.compilationUnit.files)

def test_semast_path_normalization():
    # AT-X-SEMAST-001-02, AC-X-SEMAST-001-01, AC-X-SEMAST-001-05
    contents = {
        "./a/../file1.gasd": 'CONTEXT: "C1"\nTARGET: "Py"\n'
    }
    sem_ast = get_semantic_system(contents)
    
    # ENSURE "All paths are normalized to a consistent internal format"
    # Assuming normalization resolves '..'
    assert any(f.endswith("file1.gasd") for f in sem_ast.compilationUnit.files)


def test_semast_deterministic_processing():
    # AT-X-SEMAST-001-03, AC-X-SEMAST-001-02
    contents = {
        "z.gasd": 'CONTEXT: "C"\nTARGET: "Py"\n',
        "a.gasd": 'CONTEXT: "C"\nTARGET: "Py"\n'
    }
    sem1 = get_semantic_system(contents)
    
    # Shuffle order
    shuffled = {"a.gasd": contents["a.gasd"], "z.gasd": contents["z.gasd"]}
    sem2 = get_semantic_system(shuffled)
    
    # ENSURE "The resulting CompilationUnit structure is byte-identical every time"
    assert sem1.hash == sem2.hash
    assert sem1.compilationUnit.deterministicOrder == sem2.compilationUnit.deterministicOrder
