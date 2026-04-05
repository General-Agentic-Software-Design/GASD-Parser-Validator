from enum import Enum
from typing import Dict, Any, List, Optional, Set
from .SemanticNodes import ScopeEnum

class VerificationType(Enum):
    AST_PATTERN_MATCH = "AST_PATTERN_MATCH"
    PROPERTY_BASED_TEST = "PROPERTY_BASED_TEST"
    ASSUMPTION_STATEMENT = "ASSUMPTION_STATEMENT"

class SemanticTriple:
    def __init__(self, structural: str, runtime: str, environmental: Optional[str] = None):
        self.structural = structural
        self.runtime = runtime
        self.environmental = environmental

class AnnotationDefinition:
    def __init__(self, name: str, allowed_scopes: Set[ScopeEnum], 
                 triple: SemanticTriple,
                 required_args: Set[str] = None, 
                 optional_args: Set[str] = None,
                 positional_map: List[str] = None,
                 required_string_args: Set[str] = None):
        self.name = name
        self.allowed_scopes = allowed_scopes
        self.triple = triple
        self.required_args = required_args or set()
        self.optional_args = optional_args or set()
        self.positional_map = positional_map or []
        self.required_string_args = required_string_args or set()

# Standard GEP-6 Annotation Registry (21 triples)
# Traces: #US-V2-002, #AC-V2-002-02
REGISTRY: Dict[str, AnnotationDefinition] = {
    # --- Data Validation Annotations (7) ---
    "range": AnnotationDefinition(
        "range", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Guard clause present", "Boundary inputs tested"),
        optional_args={"min", "max", "value"},
        positional_map=["min", "max", "value"]
    ),
    "min_length": AnnotationDefinition(
        "min_length", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Length guard present", "Input n-1 rejected"),
        required_args={"n"},
        positional_map=["n"]
    ),
    "max_length": AnnotationDefinition(
        "max_length", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Length guard present", "Input n+1 rejected"),
        required_args={"n"},
        positional_map=["n"]
    ),
    "format": AnnotationDefinition(
        "format", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Regex present", "Adversarial inputs handled"),
        required_args={"fmt"},
        positional_map=["fmt"]
    ),
    "unique": AnnotationDefinition(
        "unique", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Uniqueness check present", "Duplicate rejected", "DB unique constraint"),
        optional_args={"scope"},
        positional_map=["scope"]
    ),
    "default": AnnotationDefinition(
        "default", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Default assignment present", "Missing input gets val"),
        required_args={"value"},
        positional_map=["value"]
    ),
    "constraint": AnnotationDefinition(
        "constraint", {ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Validation logic present", "Violating inputs rejected"),
        required_args={"desc"},
        positional_map=["desc"]
    ),

    # --- Architectural Annotations (4) ---
    "injectable": AnnotationDefinition(
        "injectable", {ScopeEnum.TYPE, ScopeEnum.COMPONENT},
        SemanticTriple("DI constructor generated", "Component resolved from DI", "DI container configured")
    ),
    "mockable": AnnotationDefinition(
        "mockable", {ScopeEnum.TYPE, ScopeEnum.COMPONENT},
        SemanticTriple("Interface abstraction generated", "Mock substitutable")
    ),
    "transaction_type": AnnotationDefinition(
        "transaction_type", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        SemanticTriple("Transactional annotation present", "Rollback tested", "DB isolation >= READ COMMITTED"),
        required_args={"t"},
        positional_map=["t"]
    ),
    "saga": AnnotationDefinition(
        "saga", {ScopeEnum.FLOW},
        SemanticTriple("Saga pattern present", "Compensation executes", "All participants compensate")
    ),

    # --- Implementation Modifier Annotations (8) ---
    "async": AnnotationDefinition(
        "async", {ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Future/Promise return type", "Non-blocking dispatch", "Thread pool size")
    ),
    "retry": AnnotationDefinition(
        "retry", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Retry wrapper present", "Retries occur and propagate", "Idempotent OR compensation"),
        optional_args={"n"},
        positional_map=["n"]
    ),
    "timeout": AnnotationDefinition(
        "timeout", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Timeout parameter present", "TimeoutException thrown", "External service latency"),
        optional_args={"ms"},
        positional_map=["ms"]
    ),
    "external": AnnotationDefinition(
        "external", {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.STEP},
        SemanticTriple("Network error handling present", "All failure modes handled", "Endpoint reachable")
    ),
    "hash": AnnotationDefinition(
        "hash", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Named algorithm present", "Hash matches format", "Algorithm library available"),
        required_args={"algo"},
        positional_map=["algo"]
    ),
    "circuit_breaker": AnnotationDefinition(
        "circuit_breaker", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Breaker wrapper with open/half-open/closed", "FSM states tested")
    ),
    "cacheable": AnnotationDefinition(
        "cacheable", {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        SemanticTriple("Cache annotation with TTL", "Cache hit consistent within TTL", "Cache infrastructure available"),
        optional_args={"ttl"},
        positional_map=["ttl"]
    ),
    "idempotent": AnnotationDefinition(
        "idempotent", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("No side-effect duplication", "Repeated calls identical state")
    ),

    # --- Extended Annotations (2) ---
    "sensitive": AnnotationDefinition(
        "sensitive", {ScopeEnum.TYPE, ScopeEnum.FIELD},
        SemanticTriple("Field masked in logs and encryption", "Never plaintext in logs", "Encryption key management")
    ),
    "authorized": AnnotationDefinition(
        "authorized", {ScopeEnum.TYPE, ScopeEnum.COMPONENT, ScopeEnum.FLOW},
        SemanticTriple("Role check present", "Unauthorized rejected", "Auth service available"),
        required_args={"role"},
        positional_map=["role"]
    ),
    
    # Trace is a special internal annotation not in the 21 standard triples but required for mapping
    "trace": AnnotationDefinition(
        "trace", {ScopeEnum.GLOBAL, ScopeEnum.TYPE, ScopeEnum.FIELD, ScopeEnum.COMPONENT, ScopeEnum.FLOW, ScopeEnum.STEP},
        SemanticTriple("Trace directive present", "Requirement ID mapped"),
        optional_args={"value", "requirement", "id"},
        positional_map=["value", "requirement", "id"],
        required_string_args={"value", "id", "requirement"}
    ),
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
                 
    # 3. Check types for ALL provided arguments (including optional ones)
    for arg_name, val in args.items():
        if val is not None:
             if not isinstance(val, (str, int, float, bool)):
                 return f"Annotation @{name} expects a primitive argument for '{arg_name}'"
             if arg_name in defn.required_string_args and not isinstance(val, str):
                 return f"Annotation @{name} expects a string argument for '{arg_name}'"
                
    # 4. Check for unexpected args (optional)
    all_allowed = defn.required_args.union(defn.optional_args).union({"value"})
    if name == "trace":
        all_allowed.add("id")
        
    for arg_name in args:
        if arg_name not in all_allowed:
            return f"Annotation @{name} received unexpected argument '{arg_name}'"
            
    return None
