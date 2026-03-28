from typing import Dict, Any, List, Optional, Set
from .SemanticNodes import ScopeEnum

class AnnotationDefinition:
    def __init__(self, name: str, allowed_scopes: Set[ScopeEnum], 
                 required_args: Set[str] = None, 
                 optional_args: Set[str] = None):
        self.name = name
        self.allowed_scopes = allowed_scopes
        self.required_args = required_args or set()
        self.optional_args = optional_args or set()

# Standard GEP-6 Annotation Registry (21 triples)
# Triple: (Node Type/Scope, Annotation Name, Argument Schema)
REGISTRY: Dict[str, AnnotationDefinition] = {
    "trace": AnnotationDefinition(
        "trace", 
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"value"},
        optional_args={"requirement"}
    ),
    "performance": AnnotationDefinition(
        "performance",
        {ScopeEnum.FLOW, ScopeEnum.STEP},
        optional_args={"latency", "throughput"}
    ),
    "security": AnnotationDefinition(
        "security",
        {ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        optional_args={"level", "role"}
    ),
    "contract": AnnotationDefinition(
        "contract",
        {ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        required_args={"id"},
        optional_args={"invariant"}
    ),
    "environmental": AnnotationDefinition(
        "environmental",
        {ScopeEnum.STEP},
        required_args={"source"}
    ),
    "assumption": AnnotationDefinition(
        "assumption",
        {ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"condition"}
    ),
    "deprecated": AnnotationDefinition(
        "deprecated",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "experimental": AnnotationDefinition(
        "experimental",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "author": AnnotationDefinition(
        "author",
        {ScopeEnum.GLOBAL, ScopeEnum.COMPONENT},
        required_args={"name"}
    ),
    "reviewer": AnnotationDefinition(
        "reviewer",
        {ScopeEnum.GLOBAL, ScopeEnum.COMPONENT},
        required_args={"name"}
    ),
    "version": AnnotationDefinition(
        "version",
        {ScopeEnum.GLOBAL, ScopeEnum.COMPONENT},
        required_args={"value"}
    ),
    "license": AnnotationDefinition(
        "license",
        {ScopeEnum.GLOBAL},
        required_args={"name"}
    ),
    "priority": AnnotationDefinition(
        "priority",
        {ScopeEnum.GLOBAL, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"level"}
    ),
    "complexity": AnnotationDefinition(
        "complexity",
        {ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"score"}
    ),
    "resource": AnnotationDefinition(
        "resource",
        {ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"id"}
    ),
    "lifecycle": AnnotationDefinition(
        "lifecycle",
        {ScopeEnum.COMPONENT},
        required_args={"state"}
    ),
    "visibility": AnnotationDefinition(
        "visibility",
        {ScopeEnum.FIELD, ScopeEnum.COMPONENT},
        required_args={"scope"}
    ),
    "stateless": AnnotationDefinition(
        "stateless",
        {ScopeEnum.COMPONENT, ScopeEnum.FLOW}
    ),
    "idempotent": AnnotationDefinition(
        "idempotent",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "async": AnnotationDefinition(
        "async",
        {ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "blocking": AnnotationDefinition(
        "blocking",
        {ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "retry": AnnotationDefinition(
        "retry",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "timeout": AnnotationDefinition(
        "timeout",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "circuit_breaker": AnnotationDefinition(
        "circuit_breaker",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "transaction_type": AnnotationDefinition(
        "transaction_type",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    )
}

def validate_annotation_semantics(name: str, scope: ScopeEnum, args: Dict[str, Any]) -> Optional[str]:
    """
    Validates annotation against GEP-6 registry rules.
    Returns error message if invalid, None otherwise.
    """
    if name not in REGISTRY:
        # GEP-6 allows unknown annotations but they are not 'standard'
        return None
        
    defn = REGISTRY[name]
    
    # Check Scope
    if scope not in defn.allowed_scopes:
        return f"Annotation @{name} is not allowed in scope {scope.value}"
        
    # Check Required Args
    for req in defn.required_args:
        if req not in args and "value" not in args: # Support positional value as fallback for first req arg
             if req == "value" or len(defn.required_args) > 1 or "value" not in args:
                return f"Annotation @{name} requires argument '{req}'"
                
        # Type check for value/string arguments
        val = args.get(req) if req in args else args.get("value")
        if val is not None and not isinstance(val, str):
            return f"Annotation @{name} expects a string argument for '{req}'"
                
    # Check for unexpected args (optional)
    all_allowed = defn.required_args.union(defn.optional_args).union({"value"})
    for arg_name in args:
        if arg_name not in all_allowed:
            return f"Annotation @{name} received unexpected argument '{arg_name}'"
            
    return None
