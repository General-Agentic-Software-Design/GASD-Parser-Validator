from enum import Enum
from typing import Dict, List, Optional
from .SemanticNodes import SemanticNodeBase, ResolvedTypeNode, SourceRange

class SymbolKind(str, Enum):
    Type = "Type"
    Component = "Component"
    Flow = "Flow"
    Parameter = "Parameter"
    Variable = "Variable"
    Namespace = "Namespace"
    Resource = "Resource"
    Strategy = "Strategy"
    Decision = "Decision"


class SymbolEntry:
    def __init__(self, name: str, kind: SymbolKind, scope: 'SymbolScope', node_link: SemanticNodeBase, is_public: bool = True):
        self.name = name
        self.kind = kind
        self.scope = scope
        self.nodeLink = node_link
        self.isPublic = is_public
        self.isResolved = False


class SymbolScope:
    def __init__(self, scope_id: str, parent: Optional['SymbolScope'] = None):
        self.id = scope_id
        self.parent = parent
        self.symbols: Dict[str, SymbolEntry] = {}
        self.children: List['SymbolScope'] = []
        if parent:
            parent.children.append(self)


class SemanticError(Exception):
    pass


class CollisionDetector:
    def detect_collisions(self, scope: SymbolScope) -> List[SemanticError]:
        # Handled dynamically on definition in SymbolTable
        return []
        
    def detect_ambiguity(self, name: str, active_scopes: List[SymbolScope]) -> Optional[SymbolEntry]:
        # Placeholder for future multi-import ambiguity
        return None


class BuiltinTypeRegistry:
    """
    COMPONENT BuiltinTypeRegistry @trace #AC-SEMAST-019-01
    Responsible for registering and validating built-in standard types.
    """
    
    # Mapping of structural types to expected generic argument counts
    GENERIC_ARG_COUNTS = {
        "List": 1,
        "Map": 2,
        "Optional": 1,
        "Result": 1
    }

    @staticmethod
    def initializeBuiltins(symbol_table: 'SymbolTable') -> None:
        """@trace #AC-SEMAST-019-01"""
        builtins = [
            "String", "Integer", "Int", "Boolean", "Float", "Decimal", "Bytes", "UUID", 
            "DateTime", "Optional", "List", "Map", "Enum", "Result", "Any", "Void"
        ]
        
        # SourceRange for built-ins is internal
        dummy_range = SourceRange("builtin", 0, 0, 0, 0)
        
        for b in builtins:
            # Register as ResolvedTypeNodes with no fields (template markers)
            node = ResolvedTypeNode(dummy_range, b, {}, False)
            symbol_table.global_scope.symbols[b] = SymbolEntry(
                b, SymbolKind.Type, symbol_table.global_scope, node
            )

    @staticmethod
    def validateGenerics(type_name: str, arg_count: int) -> Optional[str]:
        """
        Verify generic arguments for structural types.
        Returns an error message if invalid, else None.
        @trace #AC-SEMAST-019-03
        """
        if type_name in BuiltinTypeRegistry.GENERIC_ARG_COUNTS:
            expected = BuiltinTypeRegistry.GENERIC_ARG_COUNTS[type_name]
            if arg_count != expected:
                return f"Built-in generic '{type_name}' requires {expected} type argument(s), but found {arg_count}."
        return None


class SymbolTable:
    def __init__(self):
        self.global_scope = SymbolScope("global")
        self.current_scope = self.global_scope
        self._scope_counter = 0
        BuiltinTypeRegistry.initializeBuiltins(self)

    def enter_scope(self, name: Optional[str] = None) -> SymbolScope:
        self._scope_counter += 1
        scope_name = name or f"scope_{self._scope_counter}"
        new_scope = SymbolScope(scope_name, parent=self.current_scope)
        self.current_scope = new_scope
        return new_scope

    def exit_scope(self) -> SymbolScope:
        parent = self.current_scope.parent
        if parent is None:
            raise SemanticError("Cannot exit global scope.")
        self.current_scope = parent
        return self.current_scope

    def define(self, symbol: SymbolEntry) -> None:
        if symbol.name in self.current_scope.symbols:
            raise SemanticError(f"Collision error: Symbol '{symbol.name}' is already defined in the current scope.")
            
        # Shadowing Policy: Prohibit Local-to-Global Shadowing
        # GASD prohibits shadowing common system-level types or components.
        lookup = self.resolve(symbol.name)
        if lookup and lookup.scope != self.current_scope:
            raise SemanticError(f"Shadowing error: Symbol '{symbol.name}' shadows an existing definition in an outer scope.")
            
        self.current_scope.symbols[symbol.name] = symbol

    def resolve(self, name: str, resolution_path: Optional[List[str]] = None) -> Optional[SymbolEntry]:
        path = resolution_path or []
        if name in path:
            raise SemanticError(f"CircularReference: Circular dependency detected in resolution path: {' -> '.join(path + [name])}")
        
        scope = self.current_scope
        while scope is not None:
            if name in scope.symbols:
                symbol = scope.symbols[name]
                # If we are resolving a type that might contain other types, we could add to path here if needed.
                return symbol
            scope = scope.parent
        return None

    def check_recursion(self, symbol: SymbolEntry, resolution_path: List[SymbolEntry]) -> bool:
        # AT-SEMAST-002-08
        return symbol in resolution_path
