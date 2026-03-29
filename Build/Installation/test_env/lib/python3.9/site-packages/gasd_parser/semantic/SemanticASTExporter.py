import json
from typing import List, Union
from .SemanticNodes import SemanticSystem

class SemanticASTExporter:
    """Exports Semantic AST objects to JSON format."""
    
    def to_json(self, ast: Union[SemanticSystem, List[SemanticSystem]]) -> str:
        if isinstance(ast, list):
            # Combine multiple systems into one
            combined_dict = [system.to_dict() for system in ast]
            return json.dumps(combined_dict, indent=2)
        else:
            return json.dumps(ast.to_dict(), indent=2)

    def write_to_file(self, ast: Union[SemanticSystem, List[SemanticSystem]], file_path: str):
        with open(file_path, "w") as f:
            f.write(self.to_json(ast))
