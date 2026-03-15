from typing import Dict, List, Optional
from .SemanticNodes import ResolvedNamespace, SymbolLink
from .SymbolTable import SemanticError, SymbolTable, SymbolEntry

class ImportResolver:
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.loaded_namespaces: Dict[str, ResolvedNamespace] = {}
        self.import_stack: List[str] = []

    def export_symbols(self, fqn: str, symbols: List[SymbolEntry]) -> ResolvedNamespace:
        namespace = ResolvedNamespace(fqn)
        for sym in symbols:
            # Simple assumption: all provided symbols are exported
            namespace.exportedSymbols[sym.name] = sym
        
        self.loaded_namespaces[fqn] = namespace
        return namespace

    def resolve_import(self, path: str, alias: Optional[str] = None) -> ResolvedNamespace:
        self.detect_circular_imports(path)
        
        self.import_stack.append(path)
        
        # In a real system, this would trigger file parsing if not loaded.
        # For validation, we assume the test has pre-registered it or it's a known path
        if path not in self.loaded_namespaces:
            # Mocking lazy load error
            self.import_stack.pop()
            raise SemanticError(f"NamespaceNotFound: Could not find namespace '{path}'.")
            
        namespace = self.loaded_namespaces[path]
        
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
