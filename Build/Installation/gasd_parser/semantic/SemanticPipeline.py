from typing import List, Dict, Optional, Any, Union
from ..ast.ASTNodes import (
    GASDFile, TypeDefinition, ComponentDefinition, FlowDefinition, StrategyDefinition, Decision, 
    QuestionNode, ApprovalNode, ReviewNode, FlowStepNode, TypeExpression, Parameter, MatchNode
)
from .SemanticNodes import (
    SemanticSystem, NamespaceNode, SystemMetadata, SourceRange,
    ResolvedTypeNode, ResolvedComponentNode, ResolvedFlowNode, ResolvedStrategyNode, ResolvedDecisionNode,
    ResolvedConstraintNode, ResolvedFieldNode, TypeContract, ScopeEnum, ResolvedParameter,
    ResolvedQuestionNode, ResolvedApprovalNode, ResolvedReviewNode, SymbolLink, SemanticFlowStep,
    ResolvedExpression, ResolvedMethodNode
)
from .SymbolTable import SymbolTable, SymbolEntry, SymbolKind, SemanticError
from .AnnotationResolver import AnnotationResolver
from .TypeContractBinder import BinderEngine
from .FlowAnalyzer import FlowAnalyzer
from .StrategyResolver import StrategyResolver
from .DecisionResolver import DecisionResolver
from .NamespaceResolver import NamespaceResolver
from .ImportResolver import ImportResolver
from .DirectiveResolver import DirectiveResolver
from .ResourceResolver import ResourceResolver
from .HumanInLoopResolver import HumanInLoopResolver
from .SemanticHasher import SemanticHasher
from .SemanticErrorReporter import SemanticErrorReporter, StructuredSemanticError, ErrorLevel

class SemanticPipeline:
    def __init__(self):
        self.reporter = None
        self.symbol_table = SymbolTable()
        self.annotation_resolver = AnnotationResolver()
        self.type_binder = BinderEngine(self.symbol_table)
        self.flow_analyzer = FlowAnalyzer(self.symbol_table, None)
        self.strategy_resolver = StrategyResolver()
        self.decision_resolver = DecisionResolver()
        self.namespace_resolver = NamespaceResolver()
        self.import_resolver = ImportResolver(self.symbol_table)
        self.directive_resolver = DirectiveResolver()
        self.resource_resolver = ResourceResolver()
        self.hil_resolver = HumanInLoopResolver(self.symbol_table)
        self.hasher = SemanticHasher()
        self.reporter = SemanticErrorReporter() # Reset per run
        self.flow_analyzer.reporter = self.reporter

    def get_reporter(self) -> SemanticErrorReporter:
        return self.reporter

    def _get_range(self, node: Any, file: str) -> SourceRange:
        return SourceRange(file or "", node.line, node.column, node.endLine or node.line, node.endColumn or node.column)

    def _res_type_expr(self, expr: Optional[TypeExpression]) -> Optional[TypeContract]:
        if not expr: return None
        args = [self._res_type_expr(a) for a in (expr.genericArgs or [])]
        return TypeContract(expr.baseType, args=args)

    def _res_params(self, params: List[Parameter]) -> List[ResolvedParameter]:
        return [ResolvedParameter(p.name, self._res_type_expr(p.type)) for p in params]

    def _res_match(self, node: MatchNode, file: str) -> SemanticFlowStep:
        """Resolve a MATCH node into a SemanticFlowStep tree."""
        target_expr = ResolvedExpression("String", TypeContract("String"), node.expression)
        cases = []
        for c in node.cases:
            case_step = SemanticFlowStep(
                self._get_range(node, file),
                "CASE",
                ResolvedExpression("String", TypeContract("String"), c.condition),
                {}
            )
            # MatchCase.target is currently a string representation of the result
            case_step.subSteps = [SemanticFlowStep(
                self._get_range(node, file),
                "ACTION",
                ResolvedExpression("String", TypeContract("String"), c.target),
                {}
            )]
            cases.append(case_step)
            
        return SemanticFlowStep(
            self._get_range(node, file),
            "MATCH",
            target_expr,
            {},
            sub_steps=cases
        )

    def _res_step(self, step: Any, file: str) -> SemanticFlowStep:
        if isinstance(step, MatchNode):
            return self._res_match(step, file)
            
        # Robust handling for non-FlowStepNodes (like FieldNode if it appears in flow)
        if not hasattr(step, "action") or not hasattr(step, "target"):
            name = getattr(step, "name", "unknown")
            kind = getattr(step, "kind", "UNKNOWN")
            return SemanticFlowStep(
                self._get_range(step, file),
                "DATA" if kind == "Field" else kind.upper(),
                ResolvedExpression("String", TypeContract("String"), name),
                {}
            )

        # Resolve target expression
        target = step.target
        otherwise_path = None
        
        # Handle inline OTHERWISE (e.g. ENSURE x OTHERWISE THROW y)
        if step.action == "ENSURE" and " OTHERWISE " in target:
            parts = target.split(" OTHERWISE ", 1)
            target = parts[0]
            ow_text = parts[1]
            ow_op = "THROW" if ow_text.startswith("THROW") else "RETURN"
            ow_target = ow_text[len(ow_op):].strip()
            otherwise_path = SemanticFlowStep(
                self._get_range(step, file),
                ow_op,
                ResolvedExpression("String", TypeContract("String"), ow_target),
                {}
            )
            
        target_expr = ResolvedExpression("String", TypeContract("String"), target)
        
        # Resolve bindings if any
        bindings = {}
        if hasattr(step, "asBinding") and step.asBinding and step.typePath:
             bindings[step.asBinding] = SymbolLink(step.typePath)
             
        # Resolve sub-steps
        subs = [self._res_step(s, file) for s in (getattr(step, "subSteps", []) or [])]
        
        # Handle block-level OTHERWISE from sub-steps
        for i, s in enumerate(subs):
            if s.operation == "OTHERWISE":
                ow_text = s.targetExpression.value
                ow_op = "THROW" if ow_text.startswith("THROW") else "RETURN"
                ow_target = ow_text[len(ow_op):].strip()
                otherwise_path = SemanticFlowStep(
                    s.sourceMap,
                    ow_op,
                    ResolvedExpression("String", TypeContract("String"), ow_target),
                    {}
                )
                # Remove from sub-steps as it's now in otherwise_path
                subs.pop(i)
                break

        return SemanticFlowStep(
            self._get_range(step, file),
            step.action,
            target_expr,
            bindings,
            otherwise_path=otherwise_path,
            sub_steps=subs
        )

    def run(self, ast: GASDFile) -> SemanticSystem:
        """§13. Execute the full semantic pipeline and return the enriched system AST"""
        if self.reporter is None:
            self.reporter = SemanticErrorReporter()
        self.reporter.reset()
        self.flow_analyzer.reporter = self.reporter
        try:
            return self.build([ast])
        except SemanticError as e:
            # Errors are already in reporter if raised during build analysis
            raise

    def build(self, asts: List[GASDFile]) -> SemanticSystem:
        self.reporter.reset()
        
        # Pass 1: Discovery & Registration
        for ast in asts:
            file_name = ast.sourceFile or ""
            # Types
            for t in ast.types:
                res = ResolvedTypeNode(self._get_range(t, file_name), t.name, {}, False)
                self.symbol_table.define(SymbolEntry(t.name, SymbolKind.Type, self.symbol_table.global_scope, res))
            # Components
            for c in ast.components:
                res = ResolvedComponentNode(self._get_range(c, file_name), c.name, c.pattern or "", [], [], {})
                self.symbol_table.define(SymbolEntry(c.name, SymbolKind.Component, self.symbol_table.global_scope, res))
            # Flows
            for f in ast.flows:
                res = ResolvedFlowNode(self._get_range(f, file_name), f.name, [], None, [])
                self.symbol_table.define(SymbolEntry(f.name, SymbolKind.Flow, self.symbol_table.global_scope, res))
            # Strategies
            for s in ast.strategies:
                res = ResolvedStrategyNode(self._get_range(s, file_name), s.name)
                self.symbol_table.define(SymbolEntry(s.name, SymbolKind.Strategy, self.symbol_table.global_scope, res))
            # Decisions
            for d in ast.decisions:
                res = ResolvedDecisionNode(self._get_range(d, file_name), d.name, d.chosen or "", [], None, [])
                self.symbol_table.define(SymbolEntry(d.name, SymbolKind.Decision, self.symbol_table.global_scope, res))

        # Pass 2: Resolution & Cross-linking
        for ast in asts:
            fpath = ast.sourceFile or ""
            for d in ast.directives:
                self.directive_resolver.resolve([{"kind": d.directiveType, "value": ", ".join(d.values)}])

            for t in ast.types:
                res_t: ResolvedTypeNode = self.symbol_table.resolve(t.name).nodeLink
                res_t.fields = {f.name: ResolvedFieldNode(f.name, self._res_type_expr(f.typeExpr), f.typeExpr.isOptional) for f in t.fields}
                res_t.annotations = self.annotation_resolver.resolve(t.annotations, ScopeEnum.TYPE)

            for c in ast.components:
                res_c: ResolvedComponentNode = self.symbol_table.resolve(c.name).nodeLink
                res_c.annotations = self.annotation_resolver.resolve(c.annotations, ScopeEnum.COMPONENT)
                res_c.methods = {m.name: ResolvedMethodNode(m.name, self._res_params(m.parameters), self._res_type_expr(m.returnType)) for m in c.methods}
                res_c.dependencies = [SymbolLink(d) for d in (c.dependencies or [])]

            for f in ast.flows:
                res_f: ResolvedFlowNode = self.symbol_table.resolve(f.name).nodeLink
                res_f.inputs = self._res_params(f.parameters)
                res_f.output = self._res_type_expr(f.returnType)
                res_f.pipeline = [self._res_step(s, fpath) for s in f.steps]
                res_f.annotations = self.annotation_resolver.resolve(f.annotations, ScopeEnum.FLOW)

            for s in ast.strategies:
                res_s: ResolvedStrategyNode = self.symbol_table.resolve(s.name).nodeLink
                res_s.algorithm = s.algorithm
                res_s.inputs = self._res_params(s.inputs)
                res_s.output = self._res_type_expr(s.output)

            for d in ast.decisions:
                res_d: ResolvedDecisionNode = self.symbol_table.resolve(d.name).nodeLink
                res_d.alternatives = d.alternatives or []
                res_d.rationale = d.rationale
                res_d.affectedComponents = [SymbolLink(a) for a in (d.affects or [])]

        # Pass 3: semantic Validation passes
        metadata = self.directive_resolver.resolve([])
        
        try:
            # Flow Analysis
            all_flows = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Flow]
            for f in all_flows:
                self.flow_analyzer.analyze(f)
                self.flow_analyzer.check_consistency(f)
            
            # Architecture Analysis
            from .DependencyGraphBuilder import DependencyAnalyzer
            analyzer = DependencyAnalyzer(self.symbol_table)
            all_comps = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Component]
            graph = analyzer.analyze(all_comps)
            cycles = analyzer.detect_cycles(graph)
            if cycles:
                 raise SemanticError(f"CircularDependency: {cycles[0].path}")
                 
            # Strategy Analysis
            all_strats = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Strategy]
            for s in all_strats:
                self.strategy_resolver.resolve(s)
                
            # Decision Analysis
            all_decs = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Decision]
            for d in all_decs:
                self.decision_resolver.resolve(d)

        except SemanticError as e:
            # Report and optionally re-raise depending on policy
            # For current tests we raise to match existing logic
            self.reporter.report(StructuredSemanticError(
                code="SEMAST-ERR", message=str(e), level=ErrorLevel.ERROR, 
                location=SourceRange("", 0, 0, 0, 0)
            ))
            raise

        # Package System
        types = {s.name: s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Type}
        components = {s.name: s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Component}
        flows = {s.name: s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Flow}
        strategies = {s.name: s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Strategy}
        decisions = {s.name: s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Decision}
        
        global_ns = NamespaceNode(SourceRange("", 0, 0, 0, 0), "global", types, components, flows, strategies, decisions)
        return SemanticSystem({"global": global_ns}, [], metadata)
