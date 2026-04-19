import os
import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.semantic.SemanticPipeline import SemanticPipeline

def test_authoritative_metamodel_validation():
    """
    Acceptance test: The authoritative GASD 1.2.0 specification file 
    MUST pass full semantic validation (SEMAST).
    
    This ensures that the AnnotationRegistry and SemanticPipeline 
    remain compatible with the language's own self-definition.
    """
    # Go up 4 levels to reach project root: Impl/tests/acceptance/ -> Impl/tests/ -> Impl/ -> root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metamodel_path = os.path.join(base_dir, "GASD", "GASD-1.2", "gasd-1.2.0.gasd")
    
    assert os.path.exists(metamodel_path), f"Metamodel file not found at {metamodel_path}"
    
    with open(metamodel_path, "r") as f:
        content = f.read()
        
    # 1. Parse
    api = ParseTreeAPI()
    tree, reporter = api.parse(content)
    assert not reporter.has_errors(), f"Syntax errors in metamodel: {reporter.to_console()}"
    
    # 2. AST Generation
    generator = ASTGenerator(source_file=metamodel_path)
    ast = generator.visit(tree)
    
    # 3. Semantic Pipeline (Full Cross-File Pass)
    pipeline = SemanticPipeline(validate_built_in_types=True)
    # The pipeline expects a list of ASTs (even for a single file)
    semantic_system = pipeline.run([ast])
    
    # 4. Check for Semantic Errors
    sem_rep = pipeline.get_reporter()
    errors = [e for e in sem_rep.errors if e.level.value == "ERROR"]
    
    if errors:
        error_msgs = "\n".join([f"[{err.code}] {err.message} at line {err.location.startLine}" for err in errors])
        pytest.fail(f"Authoritative metamodel failed semantic validation:\n{error_msgs}")

    assert semantic_system is not None
