from typing import Dict, Any, List, Optional
from .SemanticNodes import SemanticNodeBase, ResolvedAnnotation, ScopeEnum

class SemanticError(Exception):
    pass

class AnnotationResolver:
    def __init__(self):
        pass

    def resolve(self, syntactic_annotations: List[Any], scope: ScopeEnum) -> List[ResolvedAnnotation]:
        if not syntactic_annotations:
            return []
            
        resolved = []
        for ann in syntactic_annotations:
            args = {}
            if getattr(ann, 'arguments', None):
                for i, arg in enumerate(ann.arguments):
                    key = arg.key if hasattr(arg, 'key') and arg.key else "value"
                    val = arg.value
                    
                    # Primitive type inference
                    if val.isdigit():
                        val = int(val)
                    elif val.lstrip('-').isdigit():
                        val = int(val)
                    elif val.lower() == "true":
                        val = True
                    elif val.lower() == "false":
                        val = False
                    elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]

                    args[key] = val
                    
            res_ann = ResolvedAnnotation(ann.name, scope, args)
            self.validate(res_ann)
            resolved.append(res_ann)
            
        return resolved

    def validate(self, annotation: ResolvedAnnotation) -> None:
        if annotation.name == "trace":
            val = annotation.arguments.get("value")
            if val is not None and not isinstance(val, str):
                raise SemanticError(f"@trace annotation expects a string argument, got {type(val)}")
        elif annotation.name == "sensitive":
            pass # No specific validation defined for now
        elif annotation.name == "secure":
            pass
        elif annotation.name == "deprecated":
            pass

    def get(self, node: SemanticNodeBase, name: str, parent_node: Optional[SemanticNodeBase] = None) -> Optional[ResolvedAnnotation]:
        # Local annotation
        for ann in getattr(node, "annotations", []):
            if ann.name == name:
                return ann
                
        # Hierarchy walking if parent given
        if parent_node:
            for ann in getattr(parent_node, "annotations", []):
                if ann.name == name:
                    return ann
                    
        return None

    def get_all_inherited(self, node: SemanticNodeBase, parent_node: Optional[SemanticNodeBase] = None) -> List[ResolvedAnnotation]:
        # Merge parent and local. Local overrides parent.
        anns = {}
        if parent_node:
            for ann in getattr(parent_node, "annotations", []):
                anns[ann.name] = ann
        for ann in getattr(node, "annotations", []):
            anns[ann.name] = ann # Overrides parent
        return list(anns.values())
