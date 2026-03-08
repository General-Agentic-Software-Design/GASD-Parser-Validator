"""
AST Node Definitions based on Design/ast_design.gasd for Python 3.
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AnnotationArg:
    value: str
    key: Optional[str] = None

@dataclass
class Annotation:
    name: str
    arguments: Optional[List[AnnotationArg]] = None

@dataclass
class ASTNodeBase:
    kind: str = ""
    line: int = 0
    column: int = 0
    endLine: Optional[int] = None
    endColumn: Optional[int] = None
    sourceFile: Optional[str] = "unknown"
    annotations: Optional[List[Annotation]] = None

@dataclass
class Directive(ASTNodeBase):
    directiveType: str = "" # "CONTEXT", "TARGET", "TRACE", "NAMESPACE", "IMPORT"
    values: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    kind: str = "Directive"

@dataclass
class Decision(ASTNodeBase):
    name: str = ""
    chosen: str = ""
    kind: str = "Decision"
    rationale: Optional[str] = None
    alternatives: Optional[List[str]] = None
    affects: Optional[List[str]] = None

@dataclass
class TypeExpression(ASTNodeBase):
    baseType: str = ""
    kind: str = "TypeExpression"
    literalValue: Optional[str] = None  # GASD 1.1: holds exact literal value (e.g. "ACTIVE", 42)
    genericArgs: Optional[List['TypeExpression']] = None
    enumValues: Optional[List[str]] = None
    isOptional: bool = False

@dataclass
class FieldNode(ASTNodeBase):
    name: str = ""
    typeExpr: TypeExpression = field(default_factory=TypeExpression)
    kind: str = "Field"

@dataclass
class TypeDefinition(ASTNodeBase):
    name: str = ""
    fields: List[FieldNode] = field(default_factory=list)
    kind: str = "TypeDefinition"

@dataclass
class Parameter:
    name: str
    type: TypeExpression

@dataclass
class MethodSignature(ASTNodeBase):
    name: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    returnType: TypeExpression = field(default_factory=TypeExpression)
    kind: str = "MethodSignature"

@dataclass
class ComponentDefinition(ASTNodeBase):
    name: str = ""
    methods: List[MethodSignature] = field(default_factory=list)
    kind: str = "Component"
    pattern: Optional[str] = None
    dependencies: Optional[List[str]] = None

@dataclass
class FlowStepNode(ASTNodeBase):
    stepNumber: Optional[int] = None
    action: str = ""
    target: str = ""
    kind: str = "FlowStep"
    errorHandler: Optional[str] = None
    subSteps: Optional[List['FlowStepNode']] = None

@dataclass
class FlowDefinition(ASTNodeBase):
    name: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    steps: List[FlowStepNode] = field(default_factory=list)
    kind: str = "Flow"
    returnType: Optional[TypeExpression] = None

@dataclass
class StrategyDefinition(ASTNodeBase):
    name: str = ""
    algorithm: str = ""
    inputs: List[Parameter] = field(default_factory=list)
    output: TypeExpression = field(default_factory=TypeExpression)
    kind: str = "Strategy"
    precondition: Optional[str] = None
    complexity: Optional[str] = None

@dataclass
class ConstraintNode(ASTNodeBase):
    text: str = ""
    kind: str = "" # "Constraint" or "Invaraint"
    name: Optional[str] = None

@dataclass
class QuestionNode(ASTNodeBase):
    text: str = ""
    kind: str = "Question"
    blocking: bool = False
    context: Optional[str] = None

@dataclass
class ApprovalNode(ASTNodeBase):
    target: str = ""
    status: str = "" # "APPROVED" or "REJECTED"
    by: str = ""
    date: str = ""
    kind: str = "Approval"
    notes: Optional[str] = None

@dataclass
class TodoNode(ASTNodeBase):
    text: str = ""
    kind: str = "Todo"

@dataclass
class ReviewNode(ASTNodeBase):
    text: str = ""
    kind: str = "Review"

@dataclass
class MatchNode(ASTNodeBase):
    expression: str = ""
    cases: List['MatchCase'] = field(default_factory=list)
    kind: str = "Match"

@dataclass
class MatchCase:
    condition: str
    target: str # Can be action name, flow step, or expr

@dataclass
class EnsureNode(ASTNodeBase):
    expression: str = ""
    kind: str = "Ensure"

@dataclass
class GASDFile(ASTNodeBase):
    directives: List[Directive] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    types: List[TypeDefinition] = field(default_factory=list)
    components: List[ComponentDefinition] = field(default_factory=list)
    flows: List[FlowDefinition] = field(default_factory=list)
    strategies: List[StrategyDefinition] = field(default_factory=list)
    constraints: List[ConstraintNode] = field(default_factory=list)
    ensures: List[EnsureNode] = field(default_factory=list)
    matches: List[MatchNode] = field(default_factory=list)
    kind: str = "GASDFile"
    questions: Optional[List[QuestionNode]] = None
    approvals: Optional[List[ApprovalNode]] = None
    todos: Optional[List[TodoNode]] = None
    reviews: Optional[List[ReviewNode]] = None
