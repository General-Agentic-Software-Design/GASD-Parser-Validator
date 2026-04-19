"""
AST Exporter — Serializes the GASD AST to JSON.
Trace: #US-PARSER-007
"""

import json
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
