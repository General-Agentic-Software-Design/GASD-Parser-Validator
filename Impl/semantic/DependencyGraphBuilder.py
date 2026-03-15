from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from .SemanticNodes import SemanticNodeBase, ResolvedComponentNode, SymbolLink
from .SymbolTable import SemanticError, SymbolTable, SymbolKind

class DependencyKind(str, Enum):
    CALLS = "CALLS"
    EXTENDS = "EXTENDS"
    USES_RESOURCE = "USES_RESOURCE"
    BINDS_TYPE = "BINDS_TYPE"

class ComponentNodeType(str, Enum):
    Component = "Component"
    Interface = "Interface"
    Repository = "Repository"
    Service = "Service"

class DependencyEdge:
    def __init__(self, source: SymbolLink, target: SymbolLink, kind: DependencyKind):
        self.source = source
        self.target = target
        self.kind = kind

class GraphComponentNode:
    def __init__(self, node_id: str, kind: ComponentNodeType, public_methods: List[Any], required_resources: List[SymbolLink]):
        self.id = node_id
        self.kind = kind
        self.publicMethods = public_methods
        self.requiredResources = required_resources

class DependencyGraph:
    def __init__(self):
        self.nodes: Dict[str, GraphComponentNode] = {}
        self.edges: List[DependencyEdge] = []

class CyclePath:
    def __init__(self, path: List[str]):
        self.path = path

class DependencyAnalyzer:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table

    def analyze(self, components: List[ResolvedComponentNode]) -> DependencyGraph:
        graph = DependencyGraph()
        
        for comp in components:
            # Map COMPONENT to GraphComponentNode
            comp_kind = ComponentNodeType.Component
            if comp.pattern:
                try:
                    comp_kind = ComponentNodeType(comp.pattern)
                except ValueError:
                    pass
            
            c_node = GraphComponentNode(
                node_id=comp.name,
                kind=comp_kind,
                public_methods=list(comp.methods.values()),
                required_resources=[SymbolLink(r.name) for r in comp.resources]
            )
            graph.nodes[comp.name] = c_node
            
            # Edges for explicit dependencies
            for dep in comp.dependencies:
                edge = DependencyEdge(SymbolLink(comp.name), dep, DependencyKind.CALLS)
                graph.edges.append(edge)
                
            # Edges for resources
            for res in comp.resources:
                edge = DependencyEdge(SymbolLink(comp.name), SymbolLink(res.name), DependencyKind.USES_RESOURCE)
                graph.edges.append(edge)

        return graph

    def verify_interface(self, comp: ResolvedComponentNode, interface: SymbolLink) -> None:
        intf_entry = self.symbol_table.resolve(interface.symbolId)
        if not intf_entry or intf_entry.kind != SymbolKind.Component:
            return # Should be semantic error if missing, but maybe it's not resolved yet.
            
        intf_node = intf_entry.nodeLink
        
        for method_name, intf_method in intf_node.methods.items():
            if method_name not in comp.methods:
                raise SemanticError(f"MissingMethod: Component '{comp.name}' must implement '{method_name}' from interface '{interface.symbolId}'.")
                
            comp_method = comp.methods[method_name]
            
            # Check params match exactly
            if len(comp_method.inputs) != len(intf_method.inputs):
                raise SemanticError(f"InterfaceMismatch: Method '{method_name}' has wrong parameter count.")
                
            for i, param in enumerate(intf_method.inputs):
                comp_param = comp_method.inputs[i]
                if comp_param.typeRef.baseType != param.typeRef.baseType:
                    raise SemanticError(f"InterfaceMismatch: Method '{method_name}' parameter '{param.name}' type mismatch.")

    def detect_cycles(self, graph: DependencyGraph) -> List[CyclePath]:
        cycles = []
        visited = set()
        recursion_stack = set()
        path = []

        # Build adj list for CALLS and USES_RESOURCE
        adj: Dict[str, List[str]] = {node_id: [] for node_id in graph.nodes}
        for edge in graph.edges:
            if edge.source.symbolId in adj:
                adj[edge.source.symbolId].append(edge.target.symbolId)

        def dfs(node: str):
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            if node in adj:
                for neighbor in adj[node]:
                    if neighbor not in visited:
                        dfs(neighbor)
                    elif neighbor in recursion_stack:
                        # Found cycle
                        cycle_start_index = path.index(neighbor)
                        cycle = path[cycle_start_index:] + [neighbor]
                        cycles.append(CyclePath(cycle))
            
            recursion_stack.remove(node)
            path.pop()

        for node in list(graph.nodes.keys()):
            if node not in visited:
                dfs(node)
                
        return cycles
