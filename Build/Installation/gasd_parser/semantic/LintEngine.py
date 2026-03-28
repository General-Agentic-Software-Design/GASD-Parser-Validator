import os
import re
from typing import List, Dict, Any, Optional, Set
from .SemanticNodes import SemanticNodeBase, ResolvedAnnotation, SemanticSystem, ScopeEnum, ResolvedFlowNode, ResolvedConstraintNode
from .SemanticErrorReporter import SemanticErrorReporter, StructuredSemanticError, ErrorLevel

class LintEngine:
    def __init__(self, reporter: SemanticErrorReporter, version: str = "1.1"):
        self.reporter = reporter
        self.version = version
        self.file_versions: Dict[str, str] = {}
        self.system: Optional[SemanticSystem] = None

    def _get_version(self, node: Optional[SemanticNodeBase]) -> str:
        """Returns the version for a specific node's source file, or the system default."""
        if node and node.sourceMap and node.sourceMap.file in self.file_versions:
            return self.file_versions[node.sourceMap.file]
        return self.version

    def lint_system(self, system: SemanticSystem):
        """Runs all LINT rules across the entire semantic system."""
        self.system = system
        
        # Pass 0: Lint the system (top-level annotations/property checks)
        self.lint_node(system)
        
        # Pass 3: File-level Directives (LINT-013 Version Mismatch)
        for fnode in system.metadata.files:
            target_ver = fnode.syntacticRoot.version if fnode.syntacticRoot and hasattr(fnode.syntacticRoot, "version") else None
            if target_ver and target_ver != self.version:
                level = ErrorLevel.ERROR if self.version == "1.2" else ErrorLevel.INFO
                self._report_at("LINT-013", f"Version mismatch: File specifies GASD {target_ver} but CLI enforces {self.version}.", 1, 1, fnode.filePath, level=level)
        
        # Check for top-level postconditions (NT-GEP6-006)
        for fnode in system.metadata.files:
            file_version = self.file_versions.get(fnode.filePath, self.version)
            if file_version == "1.2":
                # Check for top-level ENSURE/POSTCONDITION in the syntactic root
                if hasattr(fnode.syntacticRoot, "ensures") and fnode.syntacticRoot.ensures:
                     self._report_at("LINT-001", "POSTCONDITION is only allowed for ACHIEVE steps in GASD 1.2.", 1, 1, fnode.filePath)
                if hasattr(fnode.syntacticRoot, "postconditions") and fnode.syntacticRoot.postconditions:
                     self._report_at("LINT-001", "POSTCONDITION is only allowed for ACHIEVE steps in GASD 1.2.", 1, 1, fnode.filePath)

        # Pass 1: Global LINT-002 check and LINT-012 Version Mismatch
        file_to_node = {f.filePath: f for f in system.metadata.files}
        for fnode in system.metadata.files:
            file_version = self.file_versions.get(fnode.filePath, self.version)
            if fnode.imports and file_version == "1.2":
                # LINT-012: Version Mismatch (NT-GEP6-007)
                has_mismatch = False
                for imp in fnode.imports:
                    imp_path = imp.get("path", "").strip("'\"")
                    imp_base = os.path.basename(imp_path)
                    
                    # Try to find the imported file in our system
                    for other_path, other_node in file_to_node.items():
                        other_base = os.path.basename(other_path)
                        if imp_base == other_base:
                            # Use explicit version check
                            other_ver = "1.1"
                            if other_node.syntacticRoot and hasattr(other_node.syntacticRoot, "version"):
                                other_ver = other_node.syntacticRoot.version or "1.1"
                            
                
                # LINT-002: Import without CONTRACT
                # Skip if there's a version mismatch (backward compatibility for legacy imports in NT-GEP6-007)
                if not system.contracts and not has_mismatch:
                     self._report_at("LINT-002", "IMPORT detected without corresponding CONTRACT in GASD 1.2.", 1, 1, fnode.filePath)

        # Pass 2: Namespace and Node-level linting
        for ns in system.namespaces.values():
            for t in ns.types.values(): self.lint_node(t)
            for c in ns.components.values():
                self.lint_node(c)
                for m in c.methods.values(): self.lint_node(m)
            for f in ns.flows.values(): 
                self._lint_flow(f)
            for d in ns.decisions.values(): self.lint_node(d)
            for s in ns.strategies.values(): self.lint_node(s)

        for cnode in system.global_constraints:
            self.lint_node(cnode)

        # GEP-6 LINT-007: CONTRACT CASE Outcome Required
        for contract in system.contracts:
            self.lint_node(contract)
            contract_version = self._get_version(contract)
            for case in getattr(contract, "cases", []):
                # Check for POSTCONDITION or THROWS or AFTER in clauses
                has_outcome = False
                clauses = getattr(case, "clauses", [])
                if not clauses and isinstance(case, dict):
                    clauses = case.get("clauses", [])
                
                if clauses:
                    # In our model, outcomes are dicts with 'type' key
                    has_outcome = any(c.get("type") in ["POSTCONDITION", "THROWS", "AFTER"] for c in clauses if isinstance(c, dict))
                
                if not has_outcome and contract_version == "1.2":
                    case_name = getattr(case, "name", "unnamed") if not isinstance(case, dict) else case.get("name", "unnamed")
                    self._report("LINT-007", f"CONTRACT CASE '{case_name}' in '{contract.name}' must have at least one outcome (POSTCONDITION, THROWS, or AFTER).", contract)

        for model in system.models:
            self.lint_node(model)
            
        for ass in system.assumptions:
            self.lint_node(ass)

    def lint_node(self, node: SemanticNodeBase):
        """Runs relevant LINT rules for a specific node."""
        aliases = set()
        
        version = self._get_version(node)
        for ann in node.annotations:
            self._check_trace_format(node, ann)
            # LINT-011: Missing 'AS' identifier in GASD 1.2
            if not ann.alias:
                # Check if it's a structural annotation that needs ID
                if ann.name in ["retry", "timeout", "circuit_breaker", "transaction_type", "idempotent", "trace"]:
                    if version == "1.2":
                        self._report("LINT-011", f"Annotation @{ann.name} is missing mandatory 'AS' identifier in GASD 1.2", node)
                    else:
                        # GASD 1.1: Info (Compatibility Hint)
                        self._report("LINT-011", f"Annotation @{ann.name} should ideally have an 'AS' identifier for GASD 1.2 compatibility.", node, ErrorLevel.INFO)

            # LINT-010: Duplicate Annotation IDs and Casing
            if ann.alias:
                if ann.alias in aliases:
                    self._report("LINT-010", f"Duplicate annotation ID '{ann.alias}' detected on node.", node)
                if version == "1.2" and not ann.alias.isupper():
                    self._report("LINT-010", f"Annotation ID '{ann.alias}' must be UPPERCASE in GASD 1.2.", node)
                aliases.add(ann.alias)

            # LINT-005: @transaction_type without ASSUMPTION (GEP-6)
            if version == "1.2" and ann.name == "transaction_type":
                has_assumption = False
                for a in (self.system.assumptions if self.system else []):
                    if "TX" in a.name or "transaction_type" in a.name or (ann.alias and ann.alias in a.name):
                        has_assumption = True
                        break
                if not has_assumption:
                    self._report("LINT-005", f"Annotation @{ann.name} must have a corresponding ASSUMPTION in GASD 1.2.", node)

            # LINT-004: @retry without @idempotent
            if version == "1.2" and ann.name == "retry":
                has_idempotent = any(a.name == "idempotent" for a in node.annotations)
                if not has_idempotent:
                    self._report("LINT-004", f"Annotation @retry requires @idempotent on the same node in GASD 1.2.", node)

            # LINT-014: Environmental dependency without ASSUMPTION (Renamed from 012)
            if version == "1.2" and ann.name in ["circuit_breaker", "timeout"]:
                has_assumption = False
                for a in (self.system.assumptions if self.system else []):
                    if (ann.alias and ann.alias in a.name) or (ann.name in a.name.lower()):
                        has_assumption = True
                        break
                if not has_assumption:
                    self._report("LINT-014", f"Annotation @{ann.name} has environmental dependencies and requires an ASSUMPTION block.", node)

        if node.kind == "Invariant":
            # LINT-003: Invariant missing SCOPE
            if not getattr(node, "scope", None):
                 if version == "1.2":
                    self._report("LINT-003", f"INVARIANT '{getattr(node, 'name', 'unnamed')}' is missing mandatory SCOPE (GLOBAL or LOCAL).", node)
                 else:
                    self._report("LINT-003", f"INVARIANT '{getattr(node, 'name', 'unnamed')}' should specify SCOPE (GLOBAL or LOCAL) for GASD 1.2 compatibility.", node, ErrorLevel.INFO)
            

    def _lint_flow(self, flow: ResolvedFlowNode):
        self.lint_node(flow)
        
        # Map all possible aliases to the internal index of the step in the pipeline
        alias_to_index = {}
        for i, step in enumerate(flow.pipeline):
             step_indices = set()
             step_id = getattr(step, "id", None)
             target_val = ""
             if hasattr(step, "targetExpression") and step.targetExpression:
                 target_val = getattr(step.targetExpression, "value", "").strip("\"'")
             step_num = getattr(step, "stepNumber", None)
             
             if step_id: step_indices.add(step_id)
             if step_num is not None: step_indices.add(str(step_num))
             if target_val: step_indices.add(target_val)
             
             for alias in list(step_indices):
                  alias_to_index[alias] = i
                  alias_to_index[f"'{alias}'"] = i
                  alias_to_index[f"\"{alias}\""] = i
        
        # Build dependency graph using internal indices
        graph = {i: [] for i in range(len(flow.pipeline))}
        for i, step in enumerate(flow.pipeline):
            for dep_id in getattr(step, "dependsOn", []) or []:
                if dep_id in alias_to_index:
                    graph[i].append(alias_to_index[dep_id])
                else:
                    clean_dep = dep_id.strip("\"'")
                    if clean_dep in alias_to_index:
                        graph[i].append(alias_to_index[clean_dep])
                    else:
                        # LINT-008: Step Dependencies Non-Existent
                        self._report("LINT-008", f"DEPENDS_ON references non-existent step '{dep_id}'", step)
        
        # LINT-009: Circular dependency
        visited = set()
        stack = set()
        
        def has_cycle(v):
            visited.add(v)
            stack.add(v)
            for neighbor in graph.get(v, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in stack:
                    return True
            stack.remove(v)
            return False

        for i in range(len(flow.pipeline)):
            if i not in visited:
                if has_cycle(i):
                    self._report("LINT-009", f"Circular dependency detected in FLOW '{flow.name}'", flow)
                    break
        
        # Normal linting pass for each step
        self._lint_steps(flow.pipeline, set(alias_to_index.keys()), flow.name)

    def _lint_steps(self, steps: List[Any], step_ids: Set[str], flow_name: str):
        for step in steps:
            version = self._get_version(step)
            op = getattr(step, "operation", "")
            has_post = any(getattr(s, "operation", "") in ["ENSURE", "POSTCONDITION"] for s in getattr(step, "subSteps", []) or [])
            if not has_post and getattr(step, "postconditions", None):
                has_post = True

            # LINT-001: ACHIEVE missing POSTCONDITION
            if op == "ACHIEVE":
                if not has_post and version == "1.2":
                    self._report("LINT-001", f"ACHIEVE step in '{flow_name}' is missing mandatory POSTCONDITION (ENSURE).", step)
                elif not has_post and version == "1.1":
                    # Info in 1.1
                    self._report("LINT-001", f"ACHIEVE step in '{flow_name}' should ideally have a POSTCONDITION (ENSURE) for GASD 1.2 compatibility.", step, ErrorLevel.INFO)
            elif has_post:
                # GEP-6 restriction: POSTCONDITION only for ACHIEVE (Error in 1.2, Info in 1.1)
                if version == "1.2":
                    self._report("LINT-001", "POSTCONDITION is only allowed for ACHIEVE steps in GASD 1.2.", step)
                else:
                    self._report("LINT-001", "POSTCONDITION is recommended only for ACHIEVE steps for GASD 1.2 compatibility.", step, ErrorLevel.INFO)

            self.lint_node(step)
            subs = getattr(step, "subSteps", []) or []
            if subs:
                self._lint_steps(subs, step_ids, flow_name)

    def _report(self, code: str, message: str, node: SemanticNodeBase, level: ErrorLevel = ErrorLevel.ERROR):
        if level == ErrorLevel.INFO and self.version == "1.1":
            return
        self.reporter.report(StructuredSemanticError(
            code=code, message=message, level=level, location=node.sourceMap
        ))

    def _report_at(self, code: str, message: str, line: int, col: int, file: str, level: ErrorLevel = ErrorLevel.ERROR):
        if level == ErrorLevel.INFO and self.version == "1.1":
            return
        from .SemanticNodes import SourceRange
        self.reporter.report(StructuredSemanticError(
            code=code, message=message, level=level, location=SourceRange(file, line, col, line, col)
        ))

    def _check_trace_format(self, node: SemanticNodeBase, ann: ResolvedAnnotation):
        if ann.name == "trace":
            val = ann.arguments.get("value")
            if val and isinstance(val, str) and not re.match(r"^#?[a-zA-Z0-9-]+$", val):
                # Reassigned from LINT-013 to LINT-015 to avoid conflict with VERSION_MISMATCH
                self._report("LINT-015", f"Trace identifier '{val}' must be alphanumeric with hyphens.", node, ErrorLevel.WARNING)
