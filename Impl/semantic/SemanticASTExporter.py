from hashlib import sha512
import json
import os
import re
from typing import List, Union, Optional, Any

from .ASTProvenance import BYTE_HASH_KEY, content_fingerprints
from .CPCInventory import VERSION as SOURCE_INVENTORY_VERSION
from .SemanticNodes import SemanticSystem

class SemanticASTExporter:
    """Exports Semantic AST objects to JSON format."""

    def __init__(self, source_paths=None):
        self.source_paths = source_paths if source_paths is not None else {}

    @staticmethod
    def source_inventory(sources):
        if not sources:
            raise ValueError("No captured sources for semantic AST export")
        for path, digest in sources.items():
            if not path or os.path.isabs(path) or not re.fullmatch(r"[0-9a-f]{128}", digest):
                raise ValueError(f"Invalid semantic AST source provenance for {path!r}")
        return {"sources": [{"path": path, "sha512": sources[path]} for path in sorted(sources)]}

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
    
    def to_json(self, ast: Union[SemanticSystem, List[SemanticSystem]], marker: Optional[dict] = None,
                *, sources=None, inventory=None) -> str:
        cwd = os.getcwd()
        provenance = self.source_inventory(sources)
        if isinstance(ast, list):
            data = [self._inject_marker_version(system.to_dict(), marker) for system in ast]
            data = self.relativize_dict(data, cwd)
            root = {"asts": data, "provenance": provenance}
            if marker and data and isinstance(data[0], dict) and "metadata" in data[0]:
                root["metadata"] = data[0]["metadata"]
        else:
            root = self.relativize_dict(self._inject_marker_version(ast.to_dict(), marker), cwd)
            root["provenance"] = provenance

        if inventory is not None:
            root["source_inventory_version"] = SOURCE_INVENTORY_VERSION
            root["source_inventory"] = inventory.reconcile(root)

        if marker:
            embedded_marker = {**marker, BYTE_HASH_KEY: "0" * 128, **content_fingerprints(root)}
            root["semantic_validate"] = embedded_marker
            # Hash the artifact with its own digest field zeroed.
            zeroed_artifact = json.dumps(root, indent=2).encode("utf-8")
            embedded_marker[BYTE_HASH_KEY] = sha512(zeroed_artifact).hexdigest()
        return json.dumps(root, indent=2)

    def relativize_dict(self, obj: Any, cwd: str) -> Any:
        """Recursively walks the object and relativizes path fields, keys, and values."""
        path_keys = {"sourceFile", "path", "filePath"}
        if isinstance(obj, dict):
            new_obj = {}
            for k, v in obj.items():
                # 1. Relativize Key (e.g. compUnit.fileNodes keys are absolute paths)
                new_k = k
                if isinstance(k, str) and os.path.isabs(k):
                    new_k = self._format_path(k, cwd)
                
                # 2. Relativize Value
                if k == "sourceMap" and isinstance(v, dict) and "file" in v:
                    # Relativize the file path in sourceMap
                    new_v = v.copy()
                    new_v["file"] = self._format_path(v["file"], cwd)
                    new_obj[new_k] = new_v
                elif k in path_keys and isinstance(v, str):
                    # Relativize standalone path fields
                    new_obj[new_k] = self._format_path(v, cwd)
                else:
                    new_obj[new_k] = self.relativize_dict(v, cwd)
            return new_obj
        elif isinstance(obj, list):
            return [self.relativize_dict(item, cwd) for item in obj]
        elif isinstance(obj, str) and os.path.isabs(obj):
            # Base case: relativize any string that is an absolute path
            return self._format_path(obj, cwd)
        else:
            return obj

    def _format_path(self, path: str, cwd: str) -> str:
        if path in self.source_paths:
            return self.source_paths[path]
        return self._do_relativize(path, cwd)

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

    def write_to_file(self, ast: Union[SemanticSystem, List[SemanticSystem]], file_path: str,
                      marker: Optional[dict] = None, *, sources=None):
        ast_bytes = self.to_json(ast, marker=marker, sources=sources).encode("utf-8")
        with open(file_path, "wb") as f:
            f.write(ast_bytes)
