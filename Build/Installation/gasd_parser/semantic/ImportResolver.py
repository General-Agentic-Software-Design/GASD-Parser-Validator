from typing import Dict, List, Optional
from .SemanticNodes import ResolvedNamespace, SymbolLink
from .SymbolTable import SemanticError, SymbolTable, SymbolEntry

class ImportResolver:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.fqn_to_namespace: Dict[str, ResolvedNamespace] = {}
        self.path_to_fqn: Dict[str, str] = {}
        self.import_stack: List[str] = []

    def export_symbols(self, fqn: str, symbols: List[SymbolEntry], path: Optional[str] = None) -> ResolvedNamespace:
        if fqn not in self.fqn_to_namespace:
            self.fqn_to_namespace[fqn] = ResolvedNamespace(fqn)
        
        namespace = self.fqn_to_namespace[fqn]
        for sym in symbols:
            # Simple assumption: all provided symbols are exported
            # Strip the FQN from sym.name if it was registered with it
            local_name = sym.name[len(fqn)+1:] if sym.name.startswith(fqn + ".") else sym.name
            namespace.exportedSymbols[local_name] = sym
        
        if path:
            self.path_to_fqn[path] = fqn
            
        return namespace

    def resolve_import(self, path_or_fqn: str, alias: Optional[str] = None) -> ResolvedNamespace:
        self.detect_circular_imports(path_or_fqn)
        
        self.import_stack.append(path_or_fqn)
        
        # Determine actual FQN
        fqn = self.path_to_fqn.get(path_or_fqn, path_or_fqn)
        
        if fqn not in self.fqn_to_namespace:
            # Mocking lazy load error
            self.import_stack.pop()
            raise SemanticError(f"NamespaceNotFound: Could not find namespace '{path_or_fqn}'.")
            
        namespace = self.fqn_to_namespace[fqn]

        
        # Apply alias if provided
        if alias:
            # Constraint AC-SEMAST-009-05: Aliases must be unique
            # In a full flow we'd check if alias already exists in current scope
            if self.symbol_table.resolve(alias):
                self.import_stack.pop()
                raise SemanticError(f"AliasCollision: Alias '{alias}' is already in use.")
            namespace.alias = alias
            
            # Register in current scope
            # Here we just mock it for the symbol table
        
        self.import_stack.pop()
        return namespace

    def detect_circular_imports(self, path: str) -> None:
        if path in self.import_stack:
            cycle = " -> ".join(self.import_stack + [path])
            raise SemanticError(f"CircularImport: Detected cyclical import dependency: {cycle}")
