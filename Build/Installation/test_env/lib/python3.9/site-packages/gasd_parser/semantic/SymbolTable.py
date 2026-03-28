from enum import Enum
from typing import Dict, List, Optional, Any, Set
from .SemanticNodes import SemanticNodeBase, ResolvedTypeNode, SourceRange, CompilationUnit, ProjectFileNode

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
    Method = "Method"


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
    def __init__(self, message: str, location: Optional[SourceRange] = None):
        super().__init__(message)
        self.location = location


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
            entry = SymbolEntry(b, SymbolKind.Type, symbol_table.global_scope, node)
            entry._builtin = True
            symbol_table.global_scope.symbols[b] = entry

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
    def __init__(self, validate_built_in_types: bool = True):
        self.global_scope = SymbolScope("global")
        self.current_scope = self.global_scope
        self._scope_counter = 0
        self.validate_built_in_types = validate_built_in_types
        BuiltinTypeRegistry.initializeBuiltins(self)

    def enter_scope(self, name: Optional[str] = None) -> SymbolScope:
        if name:
            for child in self.current_scope.children:
                if child.id == name:
                    self.current_scope = child
                    return child
                    
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
        target_scope = symbol.scope or self.current_scope
        loc = symbol.nodeLink.sourceMap if symbol.nodeLink else None
        
        existing = target_scope.symbols.get(symbol.name)
        if existing:
            if getattr(existing, '_builtin', False) and not getattr(self, 'validate_built_in_types', True):
                pass
            else:
                raise SemanticError(f"DuplicateSymbol: Collision error: Symbol '{symbol.name}' is already defined in scope '{target_scope.id}'.", location=loc)
            
        # Shadowing Policy: Prohibit Local-to-Global Shadowing
        lookup = self.resolve(symbol.name)
        if lookup and lookup.scope != target_scope:
            if getattr(lookup, '_builtin', False) and not getattr(self, 'validate_built_in_types', True):
                pass
            else:
                raise SemanticError(f"Shadowing error: Symbol '{symbol.name}' shadows a definition in scope '{lookup.scope.id}'", location=loc)
            
        target_scope.symbols[symbol.name] = symbol

    def resolve(self, name: str, resolution_path: Optional[List[str]] = None) -> Optional[SymbolEntry]:
        path = resolution_path or []
        path_tuple = tuple(path)
        if path_tuple and path_tuple[0] == path_tuple[-1]:
            raise SemanticError(f"CircularReference: Circular dependency detected in resolution path: {' -> '.join(path + [name])}")
        
        scope = self.current_scope
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
            
        # Cross-file dotted resolution: "Namespace.Symbol"
        if "." in name:
            parts = name.split(".")
            # Try to resolve the first part as a namespace or alias
            prefix = parts[0]
            ns_symbol = self.resolve(prefix)
            if ns_symbol and (ns_symbol.kind == SymbolKind.Namespace or ns_symbol.kind == SymbolKind.Component):
                remainder = ".".join(parts[1:])
                # If we have a link to the actual node, we can look deeper
                node = ns_symbol.nodeLink
                
                # AC-SEMAST-009: Aliased Dotted Resolution
                # 1. Try to resolve via FQN (if it's a namespace with an FQN)
                target_fqn = None
                if hasattr(node, "fqn"):
                    target_fqn = f"{node.fqn}.{remainder}"
                elif hasattr(node, "name") and ns_symbol.kind == SymbolKind.Component:
                    # Components can also have nested symbols (e.g. Methods, which are registered as Comp.Method)
                    target_fqn = f"{node.name}.{remainder}"
                
                if target_fqn and target_fqn in self.global_scope.symbols:
                    return self.global_scope.symbols[target_fqn]
                
                # 2. Fallback: check if the literal remains exist in global (absolute resolution)
                return self.global_scope.symbols.get(name)

        return None

    def check_recursion(self, symbol: SymbolEntry, resolution_path: List[SymbolEntry]) -> bool:
        # AT-SEMAST-002-08
        return symbol in resolution_path
