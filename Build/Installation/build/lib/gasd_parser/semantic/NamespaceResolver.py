from typing import Dict, Optional, Any, Set
from .SemanticNodes import NamespaceNode

class DependencyError(Exception):
    pass

class NamespaceResolver:
    def __init__(self):
        self.namespaces: Dict[str, NamespaceNode] = {}
        self.aliases: Dict[str, str] = {}
        self.dependencies: Dict[str, Set[str]] = {}

    def register(self, namespace: NamespaceNode, alias: Optional[str] = None):
        if namespace.name in self.namespaces:
            raise DependencyError(f"Duplicate namespace: {namespace.name}")
        self.namespaces[namespace.name] = namespace
        if alias:
            self.aliases[alias] = namespace.name

    def resolve(self, name: str) -> Optional[NamespaceNode]:
        actual_name = self.aliases.get(name, name)
        return self.namespaces.get(actual_name)

    def resolve_import(self, name: str) -> Optional[NamespaceNode]:
        return self.resolve(name)

    def resolve_symbol(self, fqn: str) -> Any:
        parts = fqn.split('.')
        ns_name = parts[0]
        ns = self.resolve(ns_name)
        if not ns:
            return None
        if len(parts) > 1 and hasattr(ns, 'types') and parts[1] in ns.types:
            return ns.types[parts[1]]
        return None

    def add_dependency(self, frm: str, to: str):
        if frm not in self.dependencies:
            self.dependencies[frm] = set()
        self.dependencies[frm].add(to)
        self.check_circular(frm, set())

    def check_circular(self, node: str, visited: Set[str]):
        if node in visited:
            raise DependencyError(f"Circular dependency detected involving {node}")
        visited.add(node)
        for dep in self.dependencies.get(node, set()):
            self.check_circular(dep, visited.copy())
