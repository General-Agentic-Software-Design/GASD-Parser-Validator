import json
from typing import List, Union, Optional
from .SemanticNodes import SemanticSystem

class SemanticASTExporter:
    """Exports Semantic AST objects to JSON format."""
    
    def to_json(self, ast: Union[SemanticSystem, List[SemanticSystem]], marker: Optional[dict] = None) -> str:
        if isinstance(ast, list):
            # Combine multiple systems into one
            data = [system.to_dict() for system in ast]
            if marker:
                # If list, we wrap in a dict to allow marker injection at root
                return json.dumps({"asts": data, "semantic_validate": marker}, indent=2)
            return json.dumps(data, indent=2)
        else:
            data = ast.to_dict()
            if marker:
                data["semantic_validate"] = marker
            return json.dumps(data, indent=2)

    def write_to_file(self, ast: Union[SemanticSystem, List[SemanticSystem]], file_path: str, marker: Optional[dict] = None):
        with open(file_path, "w") as f:
            f.write(self.to_json(ast, marker=marker))
