"""
AST Exporter — Serializes the GASD AST to JSON.
Trace: #US-PARSER-007
"""

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any

class ASTExporter:
    """
    Component responsible for serializing the AST to JSON.
    @trace #US-PARSER-007
    """

    def to_json(self, ast_node: Any, pretty_print: bool = True) -> str:
        """
        Convert a GASDFile AST into a JSON string.
        @trace #AC-PARSER-007-03, #AC-PARSER-007-08
        """
        data = self._to_dict(ast_node)
        # Relativize all paths in the data structure
        data = self.relativize_dict(data, os.getcwd())
        indent = 4 if pretty_print else None
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def _to_dict(self, obj: Any) -> Any:
        """
        Recursively convert dataclasses and lists/dicts to a JSON-serializable format.
        Ensures line/column metadata is preserved.
        """
        if is_dataclass(obj):
            # We use asdict but we can also do custom mapping if needed.
            # asdict recursively handles nested dataclasses.
            return asdict(obj)
        elif isinstance(obj, list):
            return [self._to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        else:
            return obj

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
