import json
import sys
import os
from Impl.parser.ParseTreeAPI import ParseTreeAPI
from Impl.ast.ASTGenerator import ASTGenerator
from Impl.validation.ValidationPipeline import ValidationPipeline

def run_demo(spec_path):
    print(f"=== GASD Parser Demo ===")
    print(f"Source: {spec_path}\n")
    
    api = ParseTreeAPI()
    
    # 1. Parsing
    print("[1] Parsing & Lexing...")
    with open(spec_path, 'r') as f:
        content = f.read()
    
    tree, errors = api.parse(content)
    
    if errors.get_error_count() > 0:
        print("Failure during parsing!")
        print(errors.to_console())
        return

    print("Success! Parse tree generated.\n")
    
    # 2. AST Generation
    print("[2] AST Generation...")
    generator = ASTGenerator(source_file=spec_path)
    ast = generator.visit(tree)
    print(f"AST Root: {ast.kind}")
    print(f"Entities: {len(ast.types)} Types, {len(ast.components)} Components, {len(ast.flows)} Flows")
    print(f"          {len(ast.strategies)} Strategies, {len(ast.decisions)} Decisions, {len(ast.constraints)} Constraints")
    print(f"          {len(ast.questions) if ast.questions else 0} Questions, {len(ast.approvals) if ast.approvals else 0} Approvals")
    print(f"          {len(ast.todos) if ast.todos else 0} TODOs, {len(ast.reviews) if ast.reviews else 0} Reviews\n")
    
    # 3. Semantic Validation
    print("[3] Semantic Validation...")
    pipeline = ValidationPipeline()
    semantic_errors = pipeline.validate(ast)
    
    if semantic_errors:
        print(f"Found {len(semantic_errors)} semantic issues:")
        for err in semantic_errors:
            print(f"  {err.severity}[{err.code}]: {err.message} (Line {err.line})")
    else:
        print("Validation Passed. Zero semantic errors.\n")
    
    # 4. JSON Report Output
    print("[4] Machine-Readable Report (Partial JSON):")
    report = json.loads(errors.to_json())
    # Just show metadata and first few error structures if any (though this one is valid)
    print(json.dumps({
        "success": report["success"],
        "entityCount": {
            "types": len(ast.types),
            "components": len(ast.components),
            "flows": len(ast.flows),
            "strategies": len(ast.strategies),
            "decisions": len(ast.decisions),
            "constraints": len(ast.constraints),
            "humanInLoop": (len(ast.questions) if ast.questions else 0) + (len(ast.approvals) if ast.approvals else 0)
        },
        "errorCount": report["errorCount"]
    }, indent=2))
    print("\n=== Demo Completed ===")

if __name__ == "__main__":
    target = "Specs/full_feature_demo.gasd"
    if not os.path.exists(target):
        # Create it if it doesn't exist (though it should)
        print(f"Error: {target} not found.")
    else:
        run_demo(target)
