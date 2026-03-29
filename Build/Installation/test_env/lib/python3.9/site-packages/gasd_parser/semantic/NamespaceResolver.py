from typing import Dict, Optional, Any, Set, List
from .SemanticNodes import NamespaceNode, ProjectFileNode

class DependencyError(Exception):
    pass

class NamespaceResolver:
    def __init__(self):
        self.namespaces: Dict[str, NamespaceNode] = {}
        self.aliases: Dict[str, str] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.import_graph: Dict[str, Set[str]] = {}

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
        # Support deep nesting: Core.Auth.User
        parts = fqn.split('.')
        for i in range(len(parts), 0, -1):
            prefix = '.'.join(parts[:i])
            ns = self.resolve(prefix)
            if ns:
                if i == len(parts):
                    return ns # It's the namespace itself
                remainder = parts[i:]
                # Look in types, flows, components, etc.
                for pool in [ns.types, ns.flows, ns.components, ns.strategies, ns.decisions]:
                    if remainder[0] in pool:
                        return pool[remainder[0]]
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

    def build_dependency_graph(self, compilation_unit: Any) -> Dict[str, List[str]]:
        # AT-X-SEMAST-002-03
        graph = {file_path: [imp["path"] for imp in file_node.imports] for file_path, file_node in compilation_unit.files.items()}
        return graph


    def topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        # Implementation of Kahn's or DFS-based topo sort for deterministic processing order
        result = []
        visited = set()
        temp_visited = set()

        def visit(node):
            if node in temp_visited:
                raise DependencyError(f"CircularImport: {node} is part of a cycle.")
            if node not in visited:
                temp_visited.add(node)
                for neighbor in graph.get(node, []):
                    # In GASD, imports are often namespace FQNs. 
                    # We need to map FQNs back to file paths for the graph.
                    # For this implementation, we assume graph keys are paths and neighbors are paths.
                    visit(neighbor)
                temp_visited.remove(node)
                visited.add(node)
                result.append(node)

        for node in sorted(graph.keys()):
            if node not in visited:
                visit(node)
        return result[::-1]

    def get_dependencies(self, namespace: str) -> Set[str]:
        """Return the set of namespace dependencies for a given namespace."""
        return self.dependencies.get(namespace, set())

    def get_processing_order(self, namespaces: List[str]) -> List[str]:
        """Return a topological processing order for the given namespaces."""
        graph = {ns: list(self.dependencies.get(ns, set())) for ns in namespaces}
        return self.topological_sort(graph)
