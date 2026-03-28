import os
from typing import List, Dict, Any, Optional, Union, Set
from ..ast.ASTNodes import (
    GASDFile, TypeDefinition, ComponentDefinition, FlowDefinition, StrategyDefinition, Decision, 
    QuestionNode, ApprovalNode, ReviewNode, FlowStepNode, TypeExpression, Parameter, MatchNode,
    ContractDefinition, ModelDefinition, AssumptionDefinition
)
from .SemanticNodes import (
    SemanticSystem, NamespaceNode, SystemMetadata, SourceRange, CompilationUnit, ProjectFileNode,
    ResolvedTypeNode, ResolvedComponentNode, ResolvedFlowNode, ResolvedStrategyNode, ResolvedDecisionNode,
    ResolvedConstraintNode, ResolvedFieldNode, TypeContract, ScopeEnum, ResolvedParameter,
    ResolvedQuestionNode, ResolvedApprovalNode, ResolvedReviewNode, SymbolLink, SemanticFlowStep,
    ResolvedExpression, ResolvedMethodNode, SemanticNodeBase, ResolvedAnnotation,
    ResolvedContractNode, ResolvedModelNode, ResolvedAssumptionNode
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
from .NamespaceResolver import DependencyError

class SemanticPipeline:
    def __init__(self, validate_built_in_types: bool = True):
        self.validate_built_in_types = validate_built_in_types
        self.reporter = None
        self.symbol_table = SymbolTable(validate_built_in_types=validate_built_in_types)
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
        from .ConstraintValidator import ConstraintValidator
        from .DependencyGraphBuilder import DependencyAnalyzer
        self.constraint_validator = ConstraintValidator(DependencyAnalyzer(self.symbol_table))

    def get_reporter(self) -> SemanticErrorReporter:
        return self.reporter

    def _get_range(self, node: Any, file: str) -> SourceRange:
        return SourceRange(file or "", node.line, node.column, node.endLine or node.line, node.endColumn or node.column)

    def _res_type_expr(self, expr: Optional[TypeExpression]) -> Optional[TypeContract]:
        if not expr: return None
        if expr.baseType == "List":
            if len(expr.genericArgs or []) != 1:
                raise SemanticError(f"GenericArityMismatch: 'List' requires exactly 1 type argument, got {len(expr.genericArgs or [])}")
        elif expr.baseType == "Map":
            if len(expr.genericArgs or []) != 2:
                raise SemanticError(f"GenericArityMismatch: 'Map' requires exactly 2 type arguments, got {len(expr.genericArgs or [])}")
        
        args = [self._res_type_expr(a) for a in (expr.genericArgs or [])]
        
        # GASD 1.1: Literal types (baseType == "literal") are self-resolving; skip resolution.
        # @trace #AC-X-SEMAST-004-05
        if expr.baseType in ("literal", "Record", "Enum"):
            return TypeContract(expr.baseType, args=args)

        # AC-X-SEMAST-004-04: Resolve type reference
        symbol = self.symbol_table.resolve(expr.baseType)
        if not symbol:
             # Builtins are already registered in global_scope, so if not found, it's truly unknown
             raise SemanticError(f"UnknownType: Unknown type reference: '{expr.baseType}'")
             
        # Use the canonical name (FQN) for the type reference
        return TypeContract(symbol.name, args=args)

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
            sub_steps=subs,
            postconditions=getattr(step, "postconditions", []),
            timeout=getattr(step, "timeout", None),
            depends_on=getattr(step, "dependsOn", None) or [],
            step_number=getattr(step, "stepNumber", None)
        )

    def _signatures_match(self, flow: ResolvedFlowNode, method: ResolvedMethodNode) -> bool:
        if len(flow.inputs) != len(method.inputs):
            return False
        for p1, p2 in zip(flow.inputs, method.inputs):
            t1 = getattr(p1, "typeRef", None)
            t2 = getattr(p2, "typeRef", None)
            if t1 and t2:
                if t1.baseType != t2.baseType:
                    return False
            elif t1 != t2: # Both None is OK, one None is not
                return False
        
        # Also check return type if both exist
        if flow.output and method.output:
            t1 = getattr(flow.output, "baseType", None)
            t2 = getattr(method.output, "baseType", None)
            if t1 != t2:
                return False
        elif flow.output or method.output:
            # One has return type and the other doesn't
            return False
            
        return True

    def run(self, ast: Union[GASDFile, List[GASDFile]]) -> SemanticSystem:
        """§13. Execute the full semantic pipeline and return the enriched system AST"""
        if self.reporter is None:
            self.reporter = SemanticErrorReporter()
        self.reporter.reset()
        self.flow_analyzer.reporter = self.reporter
        
        asts = [ast] if isinstance(ast, GASDFile) else ast
        
        # AC-X-SEMAST-001-03: Create CompilationUnit
        file_nodes = {}
        unknown_counter = 0
        for ast in asts:
            if ast.sourceFile and ast.sourceFile != "unknown":
                fpath = os.path.abspath(ast.sourceFile)
            else:
                fpath = f"unknown_{unknown_counter}"
                unknown_counter += 1
            # Ensure unique path keys
            while fpath in file_nodes:
                fpath = f"{fpath}_{unknown_counter}"
                unknown_counter += 1
            ns_directive = next((d for d in ast.directives if d.directiveType == "NAMESPACE"), None)
            ns_raw = ns_directive.values[0] if ns_directive and ns_directive.values else "global"
            ns_name = ns_raw.strip('"\' ').lower()
            imports = []
            for d in ast.directives:
                if d.directiveType == "IMPORT":
                    val_clean = d.values[0].strip('"\' ') if d.values else ""
                    if val_clean.endswith(".gasd") and fpath and not fpath.startswith("unknown"):
                        # Resolve relative path to absolute
                        abs_import = os.path.abspath(os.path.join(os.path.dirname(fpath), val_clean))
                        imports.append({"path": abs_import, "alias": d.alias})
                    else:
                        imports.append({"path": val_clean, "alias": d.alias})
            file_nodes[fpath] = ProjectFileNode(fpath, ns_name, imports, ast)

        
        comp_unit = CompilationUnit(file_nodes, sorted(file_nodes.keys()))
        
        # AC-X-SEMAST-002-03: Topological Sort
        dep_graph = self.namespace_resolver.build_dependency_graph(comp_unit)
        try:
            processing_order = self.namespace_resolver.topological_sort(dep_graph)
        except DependencyError as e:
            raise SemanticError(str(e))
            
        comp_unit.deterministicOrder = processing_order
        
        # AC-X-SEMAST-002: Filter processing order to only include provided files
        # Imported files not in the compilation unit will be handled by ImportResolver later
        processing_order = [f for f in processing_order if f in file_nodes]

        # Global directives aggregation
        all_directives = []
        for ast in asts:
            for d in ast.directives:
                all_directives.append({
                    "kind": d.directiveType,
                    "value": ",".join(d.values) if d.values else "",
                    "scope": "Global"
                })
        
        metadata = self.directive_resolver.resolve(all_directives)
        
        # Pass 1: Global Symbol Collection (Discovery)
        for fpath in processing_order:
            ast = file_nodes[fpath].syntacticRoot
            node = file_nodes[fpath]
            
            # Enter namespace scope
            self.symbol_table.enter_scope(node.namespace)
            # AC-X-SEMAST-003-01: Symbol Table Population
            # Define namespace in global scope if not already there
            if node.namespace not in self.symbol_table.global_scope.symbols:
                ns_res = NamespaceNode(SourceRange("", 0, 0, 0, 0), node.namespace, {}, {}, {}, {}, {})
                self.symbol_table.global_scope.symbols[node.namespace] = SymbolEntry(
                    node.namespace, SymbolKind.Namespace, self.symbol_table.global_scope, ns_res
                )
            
            # Types
            for t in ast.types:
                fqn = f"{node.namespace}.{t.name}" if node.namespace != "global" else t.name
                if self.validate_built_in_types and t.name in ["String", "Integer", "Boolean", "List", "Map", "Result"]:
                    raise SemanticError(f"BuiltinShadowingError: Cannot redefine built-in type '{t.name}'")
                
                res = ResolvedTypeNode(self._get_range(t, fpath), t.name, {}, False)
                res.fqn = fqn
                res.annotations = self.annotation_resolver.resolve(getattr(t, "annotations", []), ScopeEnum.TYPE)
                self.symbol_table.define(SymbolEntry(fqn, SymbolKind.Type, self.symbol_table.global_scope, res))
                # Local alias
                if node.namespace != "global":
                    self.symbol_table.define(SymbolEntry(t.name, SymbolKind.Type, self.symbol_table.current_scope, res))
            
            for c in ast.components:
                fqn = f"{node.namespace}.{c.name}" if node.namespace != "global" else c.name
                res_comp = ResolvedComponentNode(self._get_range(c, fpath), c.name, c.pattern or "", [], [], {})
                res_comp.fqn = fqn
                res_comp.annotations = self.annotation_resolver.resolve(getattr(c, "annotations", []), ScopeEnum.COMPONENT)
                self.symbol_table.define(SymbolEntry(fqn, SymbolKind.Component, self.symbol_table.global_scope, res_comp))
                if node.namespace != "global":
                    self.symbol_table.define(SymbolEntry(c.name, SymbolKind.Component, self.symbol_table.current_scope, res_comp))

            # Flows, Strategies, Decisions similarly...
            for f in ast.flows:
                fqn = f"{node.namespace}.{f.name}" if node.namespace != "global" else f.name
                res = ResolvedFlowNode(self._get_range(f, fpath), f.name, [], None, [])
                res.fqn = fqn
                res.annotations = self.annotation_resolver.resolve(getattr(f, "annotations", []), ScopeEnum.FLOW)
                self.symbol_table.define(SymbolEntry(fqn, SymbolKind.Flow, self.symbol_table.global_scope, res))

            for s in ast.strategies:
                fqn = f"{node.namespace}.{s.name}" if node.namespace != "global" else s.name
                res = ResolvedStrategyNode(self._get_range(s, fpath), s.name)
                res.fqn = fqn
                res.annotations = self.annotation_resolver.resolve(getattr(s, "annotations", []), ScopeEnum.FLOW) # Strategies as flows
                self.symbol_table.define(SymbolEntry(fqn, SymbolKind.Strategy, self.symbol_table.global_scope, res))

            for d in ast.decisions:
                fqn = f"{node.namespace}.{d.name}" if node.namespace != "global" else d.name
                res = ResolvedDecisionNode(self._get_range(d, fpath), d.name, d.chosen, [], [], "")
                res.fqn = fqn
                self.symbol_table.define(SymbolEntry(fqn, SymbolKind.Decision, self.symbol_table.global_scope, res))
                self.decision_resolver.resolve(res)

            # Register symbols in ImportResolver for cross-file access
            file_symbols = []
            prefix = node.namespace + "." if node.namespace != "global" else ""
            for sym_name, sym in self.symbol_table.global_scope.symbols.items():
                if sym_name.startswith(prefix) or (node.namespace == "global" and "." not in sym_name):
                    file_symbols.append(sym)
            self.import_resolver.export_symbols(node.namespace, file_symbols, fpath)

            self.symbol_table.exit_scope()

        # Pass 2: Resolution & Cross-linking
        for fpath in processing_order:
            node = file_nodes[fpath]
            ast = node.syntacticRoot
            self.symbol_table.enter_scope(node.namespace)
            
            # AC-X-SEMAST-002: Resolve imports
            for imp in node.imports:
                res_ns = self.import_resolver.resolve_import(imp["path"], imp["alias"])
                if imp["alias"]:
                    # Define alias in current scope to support Dotted Resolution: Alias.Symbol
                    self.symbol_table.define(SymbolEntry(imp["alias"], SymbolKind.Namespace, self.symbol_table.current_scope, res_ns))
            
            for t in ast.types:
                fqn = f"{node.namespace}.{t.name}" if node.namespace != "global" else t.name
                res_t: ResolvedTypeNode = self.symbol_table.resolve(fqn).nodeLink
                res_t.fields = {f.name: ResolvedFieldNode(f.name, self._res_type_expr(f.type), f.type.isOptional) for f in t.fields}
                
            for c in ast.components:
                fqn = f"{node.namespace}.{c.name}" if node.namespace != "global" else c.name
                res_c: ResolvedComponentNode = self.symbol_table.resolve(fqn).nodeLink
                res_c.methods = {
                    m.name: ResolvedMethodNode(
                        self._get_range(m, fpath), m.name, self._res_params(m.parameters), self._res_type_expr(m.returnType),
                        annotations=self.annotation_resolver.resolve(getattr(m, "annotations", []), ScopeEnum.COMPONENT)
                    ) for m in c.methods
                }
                
                # US-X-SEMAST-005 / AT-X-SEMAST-005-03: Dependency Resolution
                res_deps = []
                for dep_name in (c.dependencies or []):
                    if dep_name == "*":
                        res_deps.append(SymbolLink("*"))
                        continue
                    dep_sym = self.symbol_table.resolve(dep_name)
                    if not dep_sym or dep_sym.kind != SymbolKind.Component:
                        raise SemanticError(f"UnknownComponent: Unknown component dependency: '{dep_name}'")
                    res_deps.append(SymbolLink(dep_name))
                res_c.dependencies = res_deps
            
            for d_node in ast.decisions:
                fqn = f"{node.namespace}.{d_node.name}" if node.namespace != "global" else d_node.name
                res_d: ResolvedDecisionNode = self.symbol_table.resolve(fqn).nodeLink
                res_affects = []
                for aff in d_node.affects:
                    if aff == "*":
                        res_affects.append(SymbolLink("*"))
                        continue
                    aff_sym = self.symbol_table.resolve(aff)
                    if not aff_sym and node.namespace != "global":
                        aff_sym = self.symbol_table.resolve(f"{node.namespace}.{aff}")
                        
                    if aff_sym:
                        # SymbolLink only takes symbol_id (the FQN or name)
                        res_affects.append(SymbolLink(aff_sym.name))
                    else:
                        raise SemanticError(f"DecisionTargetError: Unknown symbol '{aff}' in DECISION {d_node.name}")
                res_d.affectedComponents = res_affects

            for f in ast.flows:
                fqn = f"{node.namespace}.{f.name}" if node.namespace != "global" else f.name
                res_f: ResolvedFlowNode = self.symbol_table.resolve(fqn).nodeLink
                res_f.inputs = self._res_params(f.parameters)
                res_f.output = self._res_type_expr(f.returnType)
                res_f.pipeline = [self._res_step(s, fpath) for s in f.steps]

            for s in ast.strategies:
                fqn = f"{node.namespace}.{s.name}" if node.namespace != "global" else s.name
                res_s: ResolvedStrategyNode = self.symbol_table.resolve(fqn).nodeLink
                res_s.inputs = self._res_params(s.inputs)
                res_s.output = self._res_type_expr(s.output)

            self.symbol_table.exit_scope()

        # Pass 3: Global Validation & GEP-6 Collections
        all_contracts = []
        all_models = []
        all_assumptions = []
        
        for fpath, fnode in file_nodes.items():
            ast = fnode.syntacticRoot
            for c in ast.contracts:
                res_c = ResolvedContractNode(self._get_range(c, fpath), c.name, list(c.behaviors.values()) if isinstance(c.behaviors, dict) else c.behaviors)
                res_c.annotations = self.annotation_resolver.resolve(getattr(c, "annotations", []), ScopeEnum.COMPONENT)
                all_contracts.append(res_c)
            for m in ast.models:
                res_m = ResolvedModelNode(self._get_range(m, fpath), m.name, getattr(m, 'fields', []), m.verifies)
                res_m.annotations = self.annotation_resolver.resolve(getattr(m, "annotations", []), ScopeEnum.COMPONENT)
                all_models.append(res_m)
            for a in ast.assumptions:
                res_a = ResolvedAssumptionNode(self._get_range(a, fpath), a.name, a.consequence)
                res_a.annotations = self.annotation_resolver.resolve(getattr(a, "annotations", []), ScopeEnum.COMPONENT)
                all_assumptions.append(res_a)

        all_flows = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s and s.kind == SymbolKind.Flow and s.nodeLink]
        all_decs = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s and s.kind == SymbolKind.Decision and s.nodeLink]
        all_comps = [s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s and s.kind == SymbolKind.Component and s.nodeLink]
        
        for f in all_flows:
            for c in all_comps:
                if f and c and hasattr(c, 'methods') and f.name in c.methods:
                    # AC-X-SEMAST-004-06: Only compare if they are in the same namespace
                    f_ns = f.fqn.rsplit('.', 1)[0] if '.' in f.fqn else "global"
                    c_ns = c.fqn.rsplit('.', 1)[0] if '.' in c.fqn else "global"
                    if f_ns != c_ns:
                        continue
                        
                    m = c.methods[f.name]
                    if not self._signatures_match(f, m):
                        raise SemanticError(f"SignatureMismatch: Flow '{f.name}' signature doesn't match component method in '{c.name}'")

        for d in all_decs:
            if d:
                self.decision_resolver.resolve(d)
        self.decision_resolver.detect_conflicts()

        # Constraints - use metadata from directives
        all_constraints = []
        for fnode in file_nodes.values():
            if not fnode or not fnode.syntacticRoot: continue
            for c_ast in fnode.syntacticRoot.constraints:
                # Resolve constraint to semantic node, preserving kind (Constraint vs Invariant)
                kind_override = getattr(c_ast, 'kind', 'ResolvedConstraint') or 'ResolvedConstraint'
                # Map AST kinds to semantic kinds
                if kind_override == 'Invariant':
                    kind_override = 'Invariant'
                res_c = ResolvedConstraintNode(SourceRange(fnode.filePath, c_ast.line, c_ast.column, c_ast.line, c_ast.column), c_ast.text, kind_override=kind_override)
                # Preserve scope and name for LINT-003/006
                res_c.scope = getattr(c_ast, 'scope', None)
                res_c.name = getattr(c_ast, 'name', None)
                all_constraints.append(res_c)
        
        # Build NamespaceNodes for ConstraintValidator/System
        # Collect all unique namespaces from file nodes
        all_ns_names = set()
        for fn in file_nodes.values():
            all_ns_names.add(fn.namespace)
        all_ns_names.add("global")  # Always ensure global is present

        ns_nodes = {}
        for ns_name in all_ns_names:
             # Find symbols for this namespace in global_scope
             prefix = ns_name + "." if ns_name != "global" else ""
             ns_types = {s.name.replace(prefix, ""): s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Type and (s.name.startswith(prefix) if prefix else "." not in s.name)}
             ns_comps = {s.name.replace(prefix, ""): s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Component and (s.name.startswith(prefix) if prefix else "." not in s.name)}
             ns_flows = {s.name.replace(prefix, ""): s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Flow and (s.name.startswith(prefix) if prefix else "." not in s.name)}
             ns_decs = {s.name.replace(prefix, ""): s.nodeLink for s in self.symbol_table.global_scope.symbols.values() if s.kind == SymbolKind.Decision and (s.name.startswith(prefix) if prefix else "." not in s.name)}
             
             source_range = SourceRange("",0,0,0,0) # Placeholder
             ns_nodes[ns_name] = NamespaceNode(source_range, ns_name, ns_types, ns_comps, ns_flows, {}, ns_decs)

        metadata.files = list(file_nodes.values())

        # Determine system version (highest version among files)
        version = "1.1"
        file_versions = {}
        for fn in file_nodes.values():
            if fn.syntacticRoot:
                fver = getattr(fn.syntacticRoot, 'version', '1.1')
                file_versions[fn.filePath] = fver
                if fver == "1.2":
                    version = "1.2"
        
        self.flow_analyzer.version = version
        
        for f in all_flows:
            if f:
                self.flow_analyzer.analyze(f)
                self.flow_analyzer.check_consistency(f)
        
        # Collect top-level annotations and postconditions
        system_annotations = []
        system_postconditions = []
        for fn in file_nodes.values():
            if fn.syntacticRoot:
                system_annotations.extend(self.annotation_resolver.resolve(fn.syntacticRoot.annotations, ScopeEnum.GLOBAL))
                system_postconditions.extend([e.expression for e in fn.syntacticRoot.ensures])
        
        system = SemanticSystem(
            ns_nodes, all_constraints, metadata, comp_unit,
            contracts=all_contracts,
            models=all_models,
            assumptions=all_assumptions,
            postconditions=system_postconditions
        )
        system.annotations = system_annotations
        
        # Pass 4: Linting Engine (GEP-6)
        from .LintEngine import LintEngine
        linter = LintEngine(self.reporter, version=version)
        linter.file_versions = file_versions
        linter.lint_system(system)
        
        from .SemanticErrorReporter import ErrorLevel
        constraint_errors = self.constraint_validator.validate_system(system)
        for msg in constraint_errors:
            self.reporter.report(StructuredSemanticError("CONSTRAINT-ERR", msg, ErrorLevel.ERROR, SourceRange("",0,0,0,0)))

        # Note: We no longer raise SemanticError here for lint violations.
        # The CLI will check the reporter for any errors.
        return system
