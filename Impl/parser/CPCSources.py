"""Resolve CLI imports before semantic validation and source verification."""

from collections import defaultdict
import os

from ..validation.ValidationPipeline import SemanticError


class CPCSources:
    def __init__(self):
        self.imports = {}

    def discover(self, source):
        imports = []
        for directive in source.directives:
            if directive.directiveType != "IMPORT" or not directive.values:
                continue
            name = directive.values[0].strip('"\' ')
            candidate = os.path.realpath(os.path.join(os.path.dirname(source.sourceFile), name))
            imports.append((directive, name, candidate if os.path.isfile(candidate) else None))
        self.imports[source.sourceFile] = imports
        return [candidate for _, _, candidate in imports if candidate is not None]

    def resolve(self, valid_asts, reporters, *, require_captured):
        captured = {path for path, _ in valid_asts}
        namespaces = defaultdict(list)
        for path, source in valid_asts:
            for directive in source.directives:
                if directive.directiveType == "NAMESPACE" and directive.values:
                    namespaces[directive.values[0].strip('"\' ').lower()].append(path)
        for path, source in valid_asts:
            source.cpc_imports = []
            for directive, name, candidate in self.imports[path]:
                target = candidate
                if target is None and not any(mark in name for mark in ("/", "\\")):
                    choices = namespaces.get(name.lower(), ())
                    target = choices[0] if choices else None
                if require_captured and target not in captured:
                    reporters[path].add_semantic_error(SemanticError(
                        code="CPC-IMPORT", severity="ERROR",
                        message=f"Could not resolve import {name!r} to a readable captured source",
                        line=directive.line, column=directive.column, sourceFile=path,
                    ))
                if target is None:
                    target = name
                    if name.endswith(".gasd"):
                        target = os.path.realpath(os.path.join(os.path.dirname(path), name))
                source.cpc_imports.append({
                    "path": target, "alias": directive.alias,
                    "sourceMap": {"file": path, "startLine": directive.line, "startCol": directive.column},
                })
