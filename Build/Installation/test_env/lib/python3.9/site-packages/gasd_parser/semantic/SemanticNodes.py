import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

class ScopeEnum(str, Enum):
    LOCAL = "LOCAL"
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
    def __init__(self, name: str, scope: ScopeEnum, arguments: Dict[str, Any], alias: Optional[str] = None):
        self.name = name
        self.scope = scope
        self.arguments = arguments
        self.alias = alias
 
    def to_dict(self):
        return {
            "name": self.name,
            "scope": self.scope.value,
            "arguments": self.arguments,
            "alias": self.alias
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
    def __init__(self, base_type: str, args: Optional[List['TypeContract']] = None, constraints: Optional[List[str]] = None, literal_value: Optional[str] = None):
        self.baseType = base_type
        self.args = args or []
        self.constraints = constraints or []
        self.literalValue = literal_value

    def to_dict(self):
        d = {
            "baseType": self.baseType,
            "args": [a.to_dict() for a in self.args],
            "constraints": self.constraints
        }
        if self.literalValue is not None:
            d["literalValue"] = self.literalValue
        return d


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
                 sub_steps: Optional[List['SemanticFlowStep']] = None,
                 postconditions: Optional[List[str]] = None,
                 timeout: Optional[str] = None,
                 depends_on: Optional[List[str]] = None,
                 step_number: Optional[int] = None):
        super().__init__("SemanticFlowStep", source_map)
        self.operation = operation
        self.targetExpression = target_expression
        self.bindings = bindings
        self.errorPath = error_path
        self.otherwisePath = otherwise_path
        self.subSteps = sub_steps or []
        self.postconditions = postconditions or []
        self.timeout = timeout
        self.dependsOn = depends_on or []
        self.stepNumber = step_number

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "operation": self.operation,
            "targetExpression": self.targetExpression.to_dict() if self.targetExpression else None,
            "bindings": {k: v.to_dict() for k, v in self.bindings.items()},
            "postconditions": self.postconditions,
            "timeout": self.timeout,
            "dependsOn": self.dependsOn,
            "stepNumber": self.stepNumber
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


class ResolvedMethodNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, inputs: List[ResolvedParameter], output: Optional[TypeContract], annotations: Optional[List[ResolvedAnnotation]] = None):
        super().__init__("ResolvedMethod", source_map, annotations=annotations)
        self.name = name
        self.inputs = inputs
        self.output = output

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "inputs": [i.to_dict() for i in self.inputs]
        })
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
                 resources: List[ResolvedResourceNode], methods: Dict[str, ResolvedMethodNode],
                 provides: Optional[List[str]] = None, requires: Optional[List[str]] = None):
        super().__init__("ResolvedComponent", source_map)
        self.name = name
        self.pattern = pattern
        self.dependencies = dependencies
        self.resources = resources
        self.methods = methods
        self.provides = provides or []
        self.requires = requires or []

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "pattern": self.pattern,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "resources": [r.to_dict() for r in self.resources],
            "methods": {k: v.to_dict() for k, v in self.methods.items()},
            "provides": self.provides,
            "requires": self.requires
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


class ResolvedNamespace(SemanticNodeBase):
    def __init__(self, fqn: str, alias: Optional[str] = None, source_map: Optional[SourceRange] = None):
        super().__init__("ResolvedNamespace", source_map or SourceRange("builtin", 0, 0, 0, 0))
        self.fqn = fqn
        self.alias = alias
        self.exportedSymbols: Dict[str, Any] = {}  # SymbolEntry
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
            "types": {k: (v.to_dict() if v is not None else None) for k, v in self.types.items()},
            "components": {k: (v.to_dict() if v is not None else None) for k, v in self.components.items()},
            "flows": {k: (v.to_dict() if v is not None else None) for k, v in self.flows.items()},
            "strategies": {k: (v.to_dict() if v is not None else None) for k, v in self.strategies.items()},
            "decisions": {k: (v.to_dict() if v is not None else None) for k, v in self.decisions.items()}
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
    def __init__(self, context: str, target: List[str], trace: List[str], files: Optional[List[Any]] = None):
        self.context = context
        self.target = target
        self.trace = trace
        self.files = files or []

    def to_dict(self):
        d = {
            "context": self.context,
            "target": self.target,
            "trace": self.trace
        }
        if self.files:
            sorted_files = sorted(self.files, key=lambda f: getattr(f, 'filePath', '') if hasattr(f, 'filePath') else str(f))
            file_dicts = []
            for f in sorted_files:
                if hasattr(f, 'to_dict'):
                    fd = f.to_dict()
                    # Remove non-deterministic fields for consistent hashing
                    fd.pop("id", None)
                    fd.pop("hash", None)
                    fd.pop("sourceMap", None)
                    file_dicts.append(fd)
                else:
                    file_dicts.append(str(f))
            d["files"] = file_dicts
        return d


class ProjectFileNode(SemanticNodeBase):
    def __init__(self, file_path: str, namespace: str, imports: List[Dict[str, str]], syntactic_root: Any):
        super().__init__("ProjectFileNode", SourceRange(file_path, 0, 0, 0, 0))
        self.filePath = file_path
        self.path = file_path  # Alias for compatibility
        self.namespace = namespace
        self.imports = imports # List of {"path": str, "alias": str}
        self.syntacticRoot = syntactic_root


    def to_dict(self):
        d = super().to_dict()
        d.update({
            "filePath": self.filePath,
            "namespace": self.namespace,
            "imports": self.imports
        })
        return d


class CompilationUnit(SemanticNodeBase):
    def __init__(self, file_nodes: Dict[str, ProjectFileNode], deterministic_order: List[str]):
        super().__init__("CompilationUnit", SourceRange("", 0, 0, 0, 0))
        self.files = file_nodes
        self.deterministicOrder = deterministic_order

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "fileNodes": {k: v.to_dict() for k, v in self.files.items()},
            "deterministicOrder": self.deterministicOrder
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

class ResolvedContractNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, cases: List[Any]):
        super().__init__("ResolvedContract", source_map)
        self.name = name
        self.cases = cases # List of cases with conditions and outcomes

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "cases": [c.to_dict() if hasattr(c, "to_dict") else str(c) for c in self.cases]
        })
        return d


class ResolvedModelNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, fields: List[Any], verifies: Optional[str] = None):
        super().__init__("ResolvedModel", source_map)
        self.name = name
        self.fields = fields
        self.verifies = verifies

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "fields": [f.to_dict() if hasattr(f, "to_dict") else str(f) for f in self.fields],
            "verifies": self.verifies
        })
        return d


class ResolvedAssumptionNode(SemanticNodeBase):
    def __init__(self, source_map: SourceRange, name: str, consequence: Optional[str] = None):
        super().__init__("ResolvedAssumption", source_map)
        self.name = name
        self.consequence = consequence

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "name": self.name,
            "name_val": self.name,
            "consequence": self.consequence
        })
        return d

class SemanticSystem(SemanticNodeBase):
    def __init__(self, namespaces: Dict[str, NamespaceNode], global_constraints: List[ResolvedConstraintNode], metadata: SystemMetadata, 
                 comp_unit: Optional[CompilationUnit] = None, 
                 contracts: Optional[List[ResolvedContractNode]] = None,
                 models: Optional[List[ResolvedModelNode]] = None,
                 assumptions: Optional[List[ResolvedAssumptionNode]] = None,
                 postconditions: Optional[List[str]] = None):
        super().__init__("SemanticSystem", SourceRange("", 0, 0, 0, 0))
        self.namespaces = namespaces
        self.global_constraints = global_constraints
        self.metadata = metadata
        self.compilationUnit = comp_unit
        self.contracts = contracts or []
        self.models = models or []
        self.assumptions = assumptions or []
        self.postconditions = postconditions or []

    def to_dict(self):
        d = super().to_dict()
        d.update({
            "namespaces": {k: v.to_dict() for k, v in self.namespaces.items()},
            "globalConstraints": [c.to_dict() for c in self.global_constraints],
            "metadata": self.metadata.to_dict(),
            "compilationUnit": self.compilationUnit.to_dict() if self.compilationUnit else None,
            "contracts": [c.to_dict() for c in self.contracts],
            "models": [m.to_dict() for m in self.models],
            "assumptions": [a.to_dict() for a in self.assumptions]
        })
        return d
