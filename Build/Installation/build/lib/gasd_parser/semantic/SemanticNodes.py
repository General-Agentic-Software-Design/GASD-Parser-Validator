import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

class ScopeEnum(str, Enum):
    GLOBAL = "GLOBAL"
    TYPE = "TYPE"
    FIELD = "FIELD"
    COMPONENT = "COMPONENT"
    FLOW = "FLOW"
    STEP = "STEP"


class SourceRange:
    def __init__(self, file: str, start_line: int, start_col: int, end_line: int, end_col: int):
        self.file = file
        self.startLine = start_line
        self.startCol = start_col
        self.endLine = end_line
        self.endCol = end_col

    def to_dict(self):
        return {
            "file": self.file,
            "startLine": self.startLine,
            "startCol": self.startCol,
            "endLine": self.endLine,
            "endCol": self.endCol
        }


class ResolvedAnnotation:
    def __init__(self, name: str, scope: ScopeEnum, arguments: Dict[str, Any]):
        self.name = name
        self.scope = scope
        self.arguments = arguments

    def to_dict(self):
        return {
            "name": self.name,
            "scope": self.scope.value,
            "arguments": self.arguments
        }


class SymbolLink:
    def __init__(self, symbol_id: str):
        self.symbolId = symbol_id

    def to_dict(self):
        return {"symbolId": self.symbolId}


class SemanticNodeBase:
    def __init__(self, kind: str, source_map: SourceRange, annotations: Optional[List[ResolvedAnnotation]] = None, documentation: Optional[str] = None):
        self.kind = kind
        self.id = str(uuid4())
        self.symbolId: Optional[str] = None
        self.sourceMap = source_map
        self.annotations = annotations or []
        self.documentation = documentation
        self._hash = None

    @property
    def hash(self) -> str:
        if not self._hash:
            d = self.to_dict()
            def clean_dict(obj):
                if isinstance(obj, dict):
                    return {k: clean_dict(v) for k, v in obj.items() if k not in ["id", "hash"]}
                elif isinstance(obj, list):
                    return [clean_dict(x) for x in obj]
                return obj
                
            cleaned_d = clean_dict(d)
            content_str = json.dumps(cleaned_d, sort_keys=True)
            self._hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        return self._hash

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "kind": self.kind,
            "id": self.id,
            "sourceMap": self.sourceMap.to_dict() if self.sourceMap else None,
            "annotations": [a.to_dict() for a in self.annotations]
        }
        if self.symbolId:
            d["symbolId"] = self.symbolId
        if self.documentation:
            d["documentation"] = self.documentation
        return d


class TypeContract:
    def __init__(self, base_type: str, args: Optional[List['TypeContract']] = None, constraints: Optional[List[str]] = None):
        self.baseType = base_type
        self.args = args or []
        self.constraints = constraints or []

    def to_dict(self):
        return {
            "baseType": self.baseType,
            "args": [a.to_dict() for a in self.args],
            "constraints": self.constraints
        }


class ResolvedFieldNode:
    def __init__(self, name: str, type_ref: TypeContract, is_optional: bool):
        self.name = name
        self.typeRef = type_ref
        self.isOptional = is_optional

    def to_dict(self):
        return {
            "name": self.name,
            "typeRef": self.typeRef.to_dict(),
            "isOptional": self.isOptional
        }


class ResolvedParameter:
    def __init__(self, name: str, type_ref: TypeContract):
        self.name = name
        self.typeRef = type_ref
        
    def to_dict(self):
        return {
            "name": self.name,
            "typeRef": self.typeRef.to_dict()
        }


class ResolvedExpression:
    def __init__(self, kind: str, type_contract: TypeContract, value: Any = None, dependencies: Optional[List[SymbolLink]] = None):
        self.kind = kind
        self.type = type_contract
        self.value = value
        self.dependencies = dependencies or []

    def to_dict(self):
        d = {
            "kind": self.kind,
            "type": self.type.to_dict(),
            "dependencies": [dep.to_dict() for dep in self.dependencies]
        }
        if self.value is not None:
            d["value"] = self.value
        return d


class SemanticFlowStep(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, operation: str, target_expression: ResolvedExpression, bindings: Dict[str, SymbolLink], 
                 error_path: Optional['SemanticFlowStep'] = None, otherwise_path: Optional['SemanticFlowStep'] = None,
                 sub_steps: Optional[List['SemanticFlowStep']] = None):
        super().__init__("SemanticFlowStep", source_map)
        self.operation = operation
        self.targetExpression = target_expression
        self.bindings = bindings
        self.errorPath = error_path
        self.otherwisePath = otherwise_path
        self.subSteps = sub_steps or []

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "operation": self.operation,
            "targetExpression": self.targetExpression.to_dict() if self.targetExpression else None,
            "bindings": {k: v.to_dict() for k, v in self.bindings.items()}
        })
        if self.errorPath:
            d["errorPath"] = self.errorPath.to_dict()
        if self.otherwisePath:
            d["otherwisePath"] = self.otherwisePath.to_dict()
        if self.subSteps:
            d["subSteps"] = [s.to_dict() for s in self.subSteps]
        return d


class ResolvedFlowNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, inputs: List[ResolvedParameter], output: Optional[TypeContract], pipeline: List[SemanticFlowStep]):
        super().__init__("ResolvedFlow", source_map)
        self.name = name
        self.inputs = inputs
        self.output = output
        self.pipeline = pipeline

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "inputs": [i.to_dict() for i in self.inputs],
            "pipeline": [p.to_dict() for p in self.pipeline]
        })
        if self.output:
            d["output"] = self.output.to_dict()
        return d


class ResolvedTypeNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, fields: Dict[str, ResolvedFieldNode], is_enum: bool,
                 enum_values: Optional[List[str]] = None, validation_binding: Optional[str] = None):
        super().__init__("ResolvedType", source_map)
        self.name = name
        self.fields = fields
        self.isEnum = is_enum
        self.enumValues = enum_values or []
        self.validationBinding = validation_binding

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "isEnum": self.isEnum
        })
        if self.enumValues:
            d["enumValues"] = self.enumValues
        if self.validationBinding:
            d["validationBinding"] = self.validationBinding
        return d


class ResolvedMethodNode:
    def __init__(self, name: str, inputs: List[ResolvedParameter], output: Optional[TypeContract]):
        self.name = name
        self.inputs = inputs
        self.output = output

    def to_dict(self):
        d = {
            "name": self.name,
            "inputs": [i.to_dict() for i in self.inputs]
        }
        if self.output:
            d["output"] = self.output.to_dict()
        return d


class ResourceKind(str, Enum):
    DB = "DB"
    API = "API"
    CACHE = "CACHE"
    STORAGE = "STORAGE"
    AUTH = "AUTH"

class ResolvedResourceNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, kind: ResourceKind, uri: Optional[str] = None, permissions: Optional[List[str]] = None):
        super().__init__("ResolvedResource", source_map)
        self.name = name
        self.resourceKind = kind
        self.uri = uri
        self.permissions = permissions or []

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "resourceKind": self.resourceKind.value,
            "permissions": self.permissions
        })
        if self.uri:
            d["uri"] = self.uri
        return d


class ResolvedComponentNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, pattern: str, dependencies: List[SymbolLink],
                 resources: List[ResolvedResourceNode], methods: Dict[str, ResolvedMethodNode]):
        super().__init__("ResolvedComponent", source_map)
        self.name = name
        self.pattern = pattern
        self.dependencies = dependencies
        self.resources = resources
        self.methods = methods

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "pattern": self.pattern,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "resources": [r.to_dict() for r in self.resources],
            "methods": {k: v.to_dict() for k, v in self.methods.items()}
        })
        return d


class AlgorithmComplexity(str, Enum):
    O1 = "O(1)"
    O_LOG_N = "O(log n)"
    ON = "O(n)"
    ON_LOG_N = "O(n log n)"
    ON2 = "O(n^2)"
    EXPONENTIAL = "O(2^n)"

class ResolvedStrategyNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, algorithm: str = "", preconditions: Optional[List[ResolvedExpression]] = None,
                 complexity: Optional[AlgorithmComplexity] = None, contract: Optional[TypeContract] = None):
        super().__init__("ResolvedStrategy", source_map)
        self.name = name
        self.algorithm = algorithm
        self.preconditions = preconditions or []
        self.complexity = complexity
        self.contract = contract

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "algorithm": self.algorithm,
            "complexity": self.complexity.value if self.complexity else None,
            "preconditions": [p.to_dict() for p in self.preconditions]
        })
        if self.contract:
            d["contract"] = self.contract.to_dict()
        return d


class ResolvedDecisionNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, chosen: str = "", rationale: str = "",
                 alternatives: Optional[List[str]] = None, affected_components: Optional[List[SymbolLink]] = None):
        super().__init__("ResolvedDecision", source_map)
        self.name = name
        self.chosen = chosen
        self.rationale = rationale
        self.alternatives = alternatives or []
        self.affectedComponents = affected_components or []

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "chosen": self.chosen,
            "rationale": self.rationale,
            "alternatives": self.alternatives,
            "affectedComponents": [c.to_dict() for c in self.affectedComponents]
        })
        return d


class ResolvedNamespace:
    def __init__(self, fqn: str, alias: Optional[str] = None):
        self.fqn = fqn
        self.alias = alias
        self.exportedSymbols: Dict[str, Any] = {} # SymbolEntry
        self.subNamespaces: Dict[str, SymbolLink] = {}

    def to_dict(self):
        return {
            "fqn": self.fqn,
            "alias": self.alias,
            "exportedSymbols": {k: v.nodeLink.to_dict() for k, v in self.exportedSymbols.items()},
            "subNamespaces": {k: v.to_dict() for k, v in self.subNamespaces.items()}
        }

class NamespaceNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, types: Dict[str, ResolvedTypeNode], components: Dict[str, ResolvedComponentNode],
                 flows: Dict[str, ResolvedFlowNode], strategies: Dict[str, ResolvedStrategyNode], decisions: Dict[str, ResolvedDecisionNode]):
        super().__init__("Namespace", source_map)
        self.name = name
        self.types = types
        self.components = components
        self.flows = flows
        self.strategies = strategies
        self.decisions = decisions

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "types": {k: v.to_dict() for k, v in self.types.items()},
            "components": {k: v.to_dict() for k, v in self.components.items()},
            "flows": {k: v.to_dict() for k, v in self.flows.items()},
            "strategies": {k: v.to_dict() for k, v in self.strategies.items()},
            "decisions": {k: v.to_dict() for k, v in self.decisions.items()}
        })
        return d


class ResolvedConstraintNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, text: str, kind_override: str = "ResolvedConstraint"):
        super().__init__(kind_override, source_map)
        self.text = text

    def to_dict(self):
        d = super().to_dict()
        d["text"] = self.text
        return d


class SystemMetadata:
    def __init__(self, context: str, target: List[str], trace: List[str]):
        self.context = context
        self.target = target
        self.trace = trace

    def to_dict(self):
        return {
            "context": self.context,
            "target": self.target,
            "trace": self.trace
        }


class SemanticSystem(SemanticNodeBase):
    def __init__(self, namespaces: Dict[str, NamespaceNode], global_constraints: List[ResolvedConstraintNode], metadata: SystemMetadata):
        # We use a dummy source map for the overall system for now.
        super().__init__("SemanticSystem", SourceRange("", 0, 0, 0, 0))
        self.namespaces = namespaces
        self.global_constraints = global_constraints
        self.metadata = metadata

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "namespaces": {k: v.to_dict() for k, v in self.namespaces.items()},
            "globalConstraints": [c.to_dict() for c in self.global_constraints],
            "metadata": self.metadata.to_dict()
        })
        return d


class ResolvedQuestionNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, text: str, is_blocking: bool = False, context: Optional[str] = None):
        super().__init__("ResolvedQuestion", source_map)
        self.text = text
        self.isBlocking = is_blocking
        self.context = context

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "text": self.text,
            "isBlocking": self.isBlocking
        })
        if self.context:
            d["context"] = self.context
        return d


class ResolvedApprovalNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, target: SymbolLink, status: str, approver: str, timestamp: str):
        super().__init__("ResolvedApproval", source_map)
        self.target = target
        self.status = status
        self.approver = approver
        self.timestamp = timestamp

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "target": self.target.to_dict(),
            "status": self.status,
            "approver": self.approver,
            "timestamp": self.timestamp
        })
        return d


class ResolvedReviewNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, text: str):
        super().__init__("ResolvedReview", source_map)
        self.text = text

    def to_dict(self):
        d = super().to_dict()
        d["text"] = self.text
        return d
