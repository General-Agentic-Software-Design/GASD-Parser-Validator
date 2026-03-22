from typing import Any, Dict, List, Optional, Set
from .SemanticNodes import SemanticNodeBase, ResolvedExpression, ResolvedTypeNode
from .SymbolTable import SymbolScope, SymbolEntry, SymbolKind


class BoundValue:
    def __init__(self, original_expr: ResolvedExpression, resolved_value: Any, type_reference: str):
        self.originalExpr = original_expr
        self.resolvedValue = resolved_value
        self.typeReference = type_reference


class BoundTypeContract:
    def __init__(self, target_type: str, bound_properties: Dict[str, BoundValue], missing_fields: List[str], extra_fields: List[str], is_valid: bool):
        self.targetType = target_type
        self.boundProperties = bound_properties
        self.missingFields = missing_fields
        self.extraFields = extra_fields
        self.isValid = is_valid


class BinderEngine:
    def __init__(self, symbol_table):
        self.symbol_table = symbol_table

    def bind(self, expr: ResolvedExpression, target: str) -> BoundTypeContract:
        from .SymbolTable import SemanticError
        # Strip generic arguments for resolution (e.g. "List<User>" → "List")
        base_target = target.split('<')[0] if '<' in target else target
        # Resolve target type
        target_entry = self.symbol_table.resolve(base_target)
        if not target_entry or target_entry.kind != SymbolKind.Type:
            if '.' in target:
                # Qualified cross-file type reference that cannot be resolved
                raise SemanticError(f"Unknown type reference: '{target}' could not be resolved across files.")
            return BoundTypeContract(target, {}, [], [], False)
            
        target_type: ResolvedTypeNode = target_entry.nodeLink
        
        # We assume expr.value is a Dictionary representation for structural binding
        source_data = expr.value if isinstance(expr.value, dict) else {}
        result = self.verify_fields(source_data, target_type)
        # For qualified types, preserve the full qualified name
        if '.' in target:
            result.targetType = target
        return result

    def verify_fields(self, source: Dict[str, Any], schema: ResolvedTypeNode, visited_types: Optional[Set[str]] = None) -> BoundTypeContract:
        visited = visited_types or set()
        if schema.name in visited:
            # AC-PARSER-004-03 / circular catch
            return BoundTypeContract(schema.name, {}, [], [], True) # Base case for circularity
            
        visited.add(schema.name)
        bound_props: Dict[str, BoundValue] = {}
        missing: List[str] = []
        extra: List[str] = list(source.keys())
        is_valid = True

        for fn, field_node in schema.fields.items():
            field_name = str(fn)
            if field_name in source:
                if field_name in extra:
                    extra.remove(field_name)
                # Sub-structure binding if the field's type is a known custom type
                val = source[field_name]
                field_type_name = field_node.typeRef.baseType
                
                # Try to resolve nested custom types
                nested_type_entry = self.symbol_table.resolve(field_type_name)
                if nested_type_entry and nested_type_entry.kind == SymbolKind.Type and isinstance(val, dict):
                    # Fixed: visited is a set, .copy() is correct, but let's be explicit
                    new_visited = set(visited)
                    nested_result = self.verify_fields(val, nested_type_entry.nodeLink, new_visited)
                    if not nested_result.isValid:
                        is_valid = False # Type mismatch in nested structure
                
                res_expr = ResolvedExpression("Literal", field_node.typeRef, val)
                bound_props[field_name] = BoundValue(res_expr, val, field_type_name)
            else:
                if not field_node.isOptional:
                    missing.append(field_name)
                    is_valid = False

        return BoundTypeContract(schema.name, bound_props, missing, extra, is_valid)

    def propagate(self, contract: BoundTypeContract, scope: SymbolScope) -> None:
        if not contract.isValid:
            return
            
        for prop_name, bound_val in contract.boundProperties.items():
            entry = SymbolEntry(prop_name, SymbolKind.Variable, scope, bound_val.originalExpr)
            # define it directly in the scope symbols to propagate
            scope.symbols[prop_name] = entry

