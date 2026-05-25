import json
import os
from typing import List, Union, Optional, Any
from .SemanticNodes import SemanticSystem

class SemanticASTExporter:
    """Exports Semantic AST objects to JSON format."""

    def _inject_marker_version(self, data: Any, marker: Optional[dict]) -> Any:
        if not marker or not isinstance(data, dict):
            return data

        gasd_file_version = marker.get("gasd_file_version")
        if not gasd_file_version:
            return data

        metadata = data.setdefault("metadata", {})
        if isinstance(metadata, dict):
            metadata["version"] = gasd_file_version
        return data
    
    def to_json(self, ast: Union[SemanticSystem, List[SemanticSystem]], marker: Optional[dict] = None) -> str:
        cwd = os.getcwd()
        if isinstance(ast, list):
            # Combine multiple systems into one
            data = [self._inject_marker_version(system.to_dict(), marker) for system in ast]
            # Relativize all paths in the data structure
            data = self.relativize_dict(data, cwd)
            
            if marker:
                # If list, we wrap in a dict to allow marker injection at root
                root = {"asts": data, "semantic_validate": marker}
                if data and isinstance(data[0], dict) and "metadata" in data[0]:
                    root["metadata"] = data[0]["metadata"]
                return json.dumps(root, indent=2)
            return json.dumps(data, indent=2)
        else:
            data = self._inject_marker_version(ast.to_dict(), marker)
            # Relativize all paths in the data structure
            data = self.relativize_dict(data, cwd)
            
            if marker:
                data["semantic_validate"] = marker
            return json.dumps(data, indent=2)

    def relativize_dict(self, obj: Any, cwd: str) -> Any:
        """Recursively walks the object and relativizes path fields, keys, and values."""
        path_keys = {"sourceFile", "path", "filePath"}
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                # 1. Relativize Key (e.g. compUnit.fileNodes keys are absolute paths)
                new_k = k
                if isinstance(k, str) and os.path.isabs(k):
                    new_k = self._do_relativize(k, cwd)
                
                # 2. Relativize Value
                if k == "sourceMap" and isinstance(v, dict) and "file" in v:
                    # Relativize the file path in sourceMap
                    new_v = v.copy()
                    new_v["file"] = self._do_relativize(v["file"], cwd)
                    new_obj[new_k] = new_v
                elif k in path_keys and isinstance(v, str):
                    # Relativize standalone path fields
                    new_obj[new_k] = self._do_relativize(v, cwd)
                else:
                    new_obj[new_k] = self.relativize_dict(v, cwd)
            return new_obj
        elif isinstance(obj, list):
            return [self.relativize_dict(item, cwd) for item in obj]
        elif isinstance(obj, str) and os.path.isabs(obj):
            # Base case: relativize any string that is an absolute path
            return self._do_relativize(obj, cwd)
        else:
            return obj

    def _do_relativize(self, path: str, cwd: str) -> str:
        if path == "stdin" or path == "<string>" or path.startswith("virtual:"):
            return path
        # Convert to absolute first to handle both relative/absolute inputs correctly
        # Use realpath to resolve symlinks (common on macOS /var -> /private/var)
        abs_file = os.path.realpath(path)
        abs_cwd = os.path.realpath(cwd)
        # Calculate relative path to CWD
        rel_file = os.path.relpath(abs_file, abs_cwd)
        # Normalize to forward slashes for portability
        return rel_file.replace("\\", "/")

    def write_to_file(self, ast: Union[SemanticSystem, List[SemanticSystem]], file_path: str, marker: Optional[dict] = None):
        with open(file_path, "w") as f:
            f.write(self.to_json(ast, marker=marker))
