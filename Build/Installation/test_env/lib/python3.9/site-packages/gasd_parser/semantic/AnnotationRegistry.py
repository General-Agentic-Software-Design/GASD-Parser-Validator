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
        optional_args={"requirement", "id"}
    ),
    "performance": AnnotationDefinition(
        "performance",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
        optional_args={"latency", "throughput"}
    ),
    "security": AnnotationDefinition(
        "security",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
        optional_args={"level", "role"}
    ),
    "contract": AnnotationDefinition(
        "contract",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW}, # Added TYPE for metamodel
        required_args={"id"},
        optional_args={"invariant"}
    ),
    "environmental": AnnotationDefinition(
        "environmental",
        {ScopeEnum.TYPE, ScopeEnum.STEP}, # Added TYPE for metamodel
        required_args={"source"}
    ),
    "assumption": AnnotationDefinition(
        "assumption",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
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
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT}, # Added TYPE for metamodel
        required_args={"name"}
    ),
    "reviewer": AnnotationDefinition(
        "reviewer",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT}, # Added TYPE for metamodel
        required_args={"name"}
    ),
    "version": AnnotationDefinition(
        "version",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT}, # Added TYPE for metamodel
        required_args={"value"}
    ),
    "license": AnnotationDefinition(
        "license",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE}, # Added TYPE for metamodel
        required_args={"name"}
    ),
    "priority": AnnotationDefinition(
        "priority",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
        required_args={"level"}
    ),
    "complexity": AnnotationDefinition(
        "complexity",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
        required_args={"score"}
    ),
    "resource": AnnotationDefinition(
        "resource",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP}, # Added TYPE for metamodel
        required_args={"id"}
    ),
    "lifecycle": AnnotationDefinition(
        "lifecycle",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT}, # Added TYPE for metamodel
        required_args={"state"}
    ),
    "visibility": AnnotationDefinition(
        "visibility",
        {ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.COMPONENT}, # Added TYPE for metamodel
        required_args={"scope"}
    ),
    "stateless": AnnotationDefinition(
        "stateless",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW} # Added TYPE for metamodel
    ),
    "idempotent": AnnotationDefinition(
        "idempotent",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "async": AnnotationDefinition(
        "async",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP} # Added TYPE for metamodel
    ),
    "blocking": AnnotationDefinition(
        "blocking",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP} # Added TYPE for metamodel
    ),
    "retry": AnnotationDefinition(
        "retry",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        optional_args={"n"}
    ),
    "timeout": AnnotationDefinition(
        "timeout",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        optional_args={"ms"}
    ),
    "circuit_breaker": AnnotationDefinition(
        "circuit_breaker",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP}
    ),
    "transaction_type": AnnotationDefinition(
        "transaction_type",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        optional_args={"t"}
    ),
    "optimize": AnnotationDefinition(
        "optimize",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        required_args={"goal"}
    ),
    "error_strategy": AnnotationDefinition(
        "error_strategy",
        {ScopeEnum.TYPE, ScopeEnum.FLOW},
        required_args={"strategy"}
    ),
    "algorithm": AnnotationDefinition(
        "algorithm",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"name"}
    ),
    "hash": AnnotationDefinition(
        "hash",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        required_args={"algo"}
    ),
    "status": AnnotationDefinition(
        "status",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT},
        required_args={"s"}
    ),
    "agent_note": AnnotationDefinition(
        "agent_note",
        {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"txt"}
    ),
    "heuristic": AnnotationDefinition(
        "heuristic",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"txt"}
    ),
    "metric": AnnotationDefinition(
        "metric",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        required_args={"name"}
    ),
    "trace_id": AnnotationDefinition(
        "trace_id",
        {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP},
        required_args={"val"}
    ),
    "cacheable": AnnotationDefinition(
        "cacheable",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        optional_args={"ttl"}
    ),
    "index": AnnotationDefinition(
        "index",
        {ScopeEnum.TYPE, ScopeEnum.FIELD}
    ),
    "transient": AnnotationDefinition(
        "transient",
        {ScopeEnum.TYPE, ScopeEnum.FIELD}
    ),
    "rest": AnnotationDefinition(
        "rest",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        required_args={"verb", "path"}
    ),
    # Missing GEP-6 Data Validation Annotations
    "range": AnnotationDefinition(
        "range",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        optional_args={"min", "max"}
    ),
    "min_length": AnnotationDefinition(
        "min_length",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        required_args={"n"}
    ),
    "max_length": AnnotationDefinition(
        "max_length",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        required_args={"n"}
    ),
    "format": AnnotationDefinition(
        "format",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        required_args={"fmt"}
    ),
    "unique": AnnotationDefinition(
        "unique",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        optional_args={"scope"}
    ),
    "default": AnnotationDefinition(
        "default",
        {ScopeEnum.TYPE, ScopeEnum.FIELD},
        required_args={"value"}
    ),
    "injectable": AnnotationDefinition(
        "injectable",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT}
    ),
    "mockable": AnnotationDefinition(
        "mockable",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT}
    ),
    "external": AnnotationDefinition(
        "external",
        {ScopeEnum.TYPE, ScopeEnum.COMPONENT}
    ),
    "sensitive": AnnotationDefinition(
        "sensitive",
        {ScopeEnum.TYPE, ScopeEnum.FIELD}
    ),
    "mask": AnnotationDefinition(
        "mask",
        {ScopeEnum.TYPE, ScopeEnum.FIELD}
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
        # Special case for @trace: 'id' can substitute for 'value' in metamodels
        effective_key = None
        if req in args:
            effective_key = req
        elif "value" in args:
            effective_key = "value"
        elif name == "trace" and req == "value" and "id" in args:
            effective_key = "id"
            
        if not effective_key:
            return f"Annotation @{name} requires argument '{req}'"
                
        # Type check for value/string arguments
        val = args[effective_key]
        if val is not None and not isinstance(val, str):
            return f"Annotation @{name} expects a string argument for '{req}'"
                
    # Check for unexpected args (optional)
    all_allowed = defn.required_args.union(defn.optional_args).union({"value"})
    if name == "trace":
        all_allowed.add("id")
        
    for arg_name in args:
        if arg_name not in all_allowed:
            return f"Annotation @{name} received unexpected argument '{arg_name}'"
            
    return None
