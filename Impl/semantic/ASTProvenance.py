"""Version 1 projection and reporting for validated semantic AST exports."""

from collections import Counter
from hashlib import sha512
import json


CONTENT_VERSION = "1"

_ROOT_METADATA = {"provenance", "semantic_validate", "compilationUnit"}
_SYNTAX_LOCATIONS = {"sourceFile", "line", "column", "endLine", "endColumn"}
_UNORDERED_ROOT = {"globalConstraints", "contracts", "models", "assumptions"}
_UNORDERED_FIELDS = {
    "SemanticFlowStep": {"dependsOn"},
    "ResolvedComponent": {"dependencies", "resources", "provides", "requires"},
    "ResolvedDecision": {"affectedComponents"},
    "ResolvedAssumption": {"affected"},
    "ResolvedResource": {"permissions"},
}


def _encode(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _semantic_root(artifact):
    root = {key: value for key, value in artifact.items() if key not in _ROOT_METADATA}
    if "metadata" in root:
        root["metadata"] = {key: value for key, value in root["metadata"].items() if key != "files"}

    files = (artifact.get("compilationUnit") or {}).get("fileNodes", {})
    edges = {}
    for source in files.values():
        for dependency in source["imports"]:
            path = dependency["path"]
            target = {"namespace": files[path]["namespace"]} if path in files else {"external": path}
            edge = {"namespace": source["namespace"], "alias": dependency.get("alias"), "target": target}
            edges[_encode(edge)] = edge
    if edges:
        root["imports"] = [edges[key] for key in sorted(edges)]
    return root


def _generated_id(node):
    if isinstance(node.get("kind"), str) and isinstance(node.get("id"), str):
        return node["id"]
    return None


def _semantic_fields(node):
    kind = node.get("kind")
    omitted = set()
    if isinstance(kind, str):
        if "id" in node or "sourceMap" in node:
            omitted.update(("id", "sourceMap"))
        if kind == "ResolvedContract":
            omitted.add("hash")
        omitted.update(_SYNTAX_LOCATIONS)
    return ((key, value) for key, value in node.items() if key not in omitted)


def _is_annotation_payload(node, key):
    return key == "arguments" and isinstance(node.get("name"), str)


def _unordered_fields(node, path):
    if not path:
        return _UNORDERED_ROOT
    if path == ["metadata"]:
        return {"target", "trace"}
    kind = node.get("kind")
    if not isinstance(kind, str):
        return ()
    if "type" in node and "dependencies" in node:
        return {"dependencies"}
    return _UNORDERED_FIELDS.get(kind, ())


def _walk_nodes(value):
    if isinstance(value, dict):
        yield value
        for key, child in _semantic_fields(value):
            if not _is_annotation_payload(value, key):
                yield from _walk_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_nodes(child)


class _Projection:
    def __init__(self, root):
        self.generated_ids = {identifier for node in _walk_nodes(root) if (identifier := _generated_id(node))}
        self.paths = {}
        self._index_paths(root, [])

    def _index_paths(self, value, path, unordered=False):
        if isinstance(value, dict):
            identifier = _generated_id(value)
            if identifier is not None:
                previous = self.paths.get(identifier)
                if previous is None or _encode(path) < _encode(previous):
                    self.paths[identifier] = path
            unordered_fields = _unordered_fields(value, path)
            for key, child in _semantic_fields(value):
                if not _is_annotation_payload(value, key):
                    self._index_paths(child, [*path, key], key in unordered_fields)
        elif isinstance(value, list):
            segments = self._member_segments(value) if unordered else range(len(value))
            for segment, member in zip(segments, value):
                self._index_paths(member, [*path, segment])

    def _member_segments(self, members):
        labels = [
            (member.get("kind"), member.get("name") or member.get("text"))
            if isinstance(member, dict) else (None, None)
            for member in members
        ]
        counts = Counter(_encode(label) for label in labels)
        for label, member in zip(labels, members):
            segment = list(label)
            if label[1] is None or counts[_encode(label)] > 1:
                segment.append(self.normalize(member, [segment], shape_only=True))
            yield segment

    def normalize(self, value, path, *, shape_only=False):
        if isinstance(value, list):
            return [self.normalize(item, [*path, index], shape_only=shape_only)
                    for index, item in enumerate(value)]
        if not isinstance(value, dict):
            return value

        unordered_fields = _unordered_fields(value, path)
        result = {}
        for key, child in _semantic_fields(value):
            if _is_annotation_payload(value, key):
                result[key] = child
            elif key == "symbolId" and isinstance(child, str) and child in self.generated_ids:
                result[key] = None if shape_only else {"node": self.paths[child]}
            else:
                projected = self.normalize(child, [*path, key], shape_only=shape_only)
                if key in unordered_fields and isinstance(projected, list):
                    projected.sort(key=_encode)
                result[key] = projected
        return result


def canonical_content(artifact):
    """Return the UTF-8 JSON bytes for content fingerprint rules version 1."""
    root = _semantic_root(artifact)
    return _encode(_Projection(root).normalize(root, []))


def fingerprints(delivered_bytes, canonical_bytes):
    return {
        "semantic_ast_bytes_sha512": sha512(delivered_bytes).hexdigest(),
        "semantic_ast_content_sha512": sha512(canonical_bytes).hexdigest(),
        "semantic_ast_content_version": CONTENT_VERSION,
    }
