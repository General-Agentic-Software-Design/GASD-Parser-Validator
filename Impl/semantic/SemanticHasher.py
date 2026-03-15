from typing import List, Dict, Any
from .SemanticNodes import SemanticNodeBase, SemanticSystem

class DriftReport:
    def __init__(self, node_id: str, kind: str, message: str):
        self.nodeId = node_id
        self.kind = kind
        self.message = message

class SemanticHasher:
    def compute_hash(self, node: SemanticNodeBase) -> str:
        # Relies on the deterministic property hash built into SemanticNodeBase
        return node.hash

    def _flatten_tree(self, node: SemanticNodeBase, flat_map: Dict[str, SemanticNodeBase]):
        flat_map[node.id] = node
        
        # We recursively find child nodes that inherit from SemanticNodeBase
        d = node.to_dict()
        self._find_nodes_in_dict(d, flat_map)
        
    def _find_nodes_in_dict(self, obj: Any, flat_map: Dict[str, SemanticNodeBase]):
        if isinstance(obj, SemanticNodeBase):
            self._flatten_tree(obj, flat_map)
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, SemanticNodeBase):
                    self._flatten_tree(v, flat_map)
                elif isinstance(v, (dict, list)):
                    self._find_nodes_in_dict(v, flat_map)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, SemanticNodeBase):
                    self._flatten_tree(item, flat_map)
                elif isinstance(item, (dict, list)):
                    self._find_nodes_in_dict(item, flat_map)

    def compare(self, old_state: SemanticSystem, new_state: SemanticSystem) -> List[DriftReport]:
        reports = []
        
        if old_state.hash == new_state.hash:
            return reports
            
        old_map: Dict[str, str] = {}
        new_map: Dict[str, str] = {}
        
        # In a real impl, we'd recursively flatten everything and map NodeID -> Hash
        # But for simplistic testing, we'll just check root and maybe direct children namespaces
        
        for ns_name, ns_node in old_state.namespaces.items():
            old_map[ns_name] = ns_node.hash
        for ns_name, ns_node in new_state.namespaces.items():
            new_map[ns_name] = ns_node.hash
            
        for name, hsh in old_map.items():
            if name not in new_map:
                reports.append(DriftReport(name, "Namespace", "Deleted"))
            elif new_map[name] != hsh:
                reports.append(DriftReport(name, "Namespace", "Modified"))
                
        for name in new_map:
            if name not in old_map:
                reports.append(DriftReport(name, "Namespace", "Added"))
                
        return reports

class DeterminismGuard:
    def verify_runs(self, *states: SemanticSystem) -> bool:
        if not states:
            return True
            
        base_hash = states[0].hash
        for state in states[1:]:
            if state.hash != base_hash:
                return False
                
        return True
