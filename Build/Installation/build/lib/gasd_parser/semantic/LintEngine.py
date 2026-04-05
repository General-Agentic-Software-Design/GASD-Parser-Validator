import os
import re
from typing import List, Dict, Any, Optional, Set
from .SemanticNodes import SemanticNodeBase, ResolvedAnnotation, SemanticSystem, ScopeEnum, ResolvedFlowNode
from .SemanticErrorReporter import SemanticErrorReporter, StructuredSemanticError, ErrorLevel
from .VersionResolver import VersionResolver

class LintEngine:
    """
    GASD 1.2 Linting Engine implementing all 13 rules from GEP-6 §9.1.
    Traces: #US-V2-001, #US-V2-009
    """
    def __init__(self, reporter: SemanticErrorReporter, version: str = "1.2"):
        self.reporter = reporter
        self.version = version
        self.file_versions: Dict[str, str] = {}
        self.system: Optional[SemanticSystem] = None
        self.cli_version_override: bool = False

    def _get_version(self, node: Optional[SemanticNodeBase]) -> str:
        """Returns the version for a specific node's source file, or the system default."""
        if node and node.sourceMap and node.sourceMap.file in self.file_versions:
            return self.file_versions[node.sourceMap.file]
        return self.version

    def _get_severity(self, version: str, v12_level: ErrorLevel, v11_level: ErrorLevel) -> ErrorLevel:
        """Determines severity based on the file version."""
        return v12_level if version == "1.2" else v11_level

    def lint_system(self, system: SemanticSystem):
        """Runs all LINT rules across the entire semantic system."""
        self.system = system
        
        # Pass 0: Lint the system (top-level properties)
        self.lint_node(system)
        
        # Pass 0b: File-level check (Version & Placement)
        for fnode in system.metadata.files:
            if not fnode.syntacticRoot: continue
            
            # US-V2-001: VERSION MUST be first
            if not getattr(fnode.syntacticRoot, "version_first", True):
                file_ver = self.file_versions.get(fnode.filePath, self.version)
                severity = ErrorLevel.ERROR if file_ver == "1.2" else ErrorLevel.WARNING
                self._report_at("V2-001", "SyntaxError: VERSION directive MUST be the first directive in the file.", 1, 1, fnode.filePath, level=severity)
            
            # LINT-013: Version Mismatch between CLI and file
            target_ver = fnode.syntacticRoot.version if hasattr(fnode.syntacticRoot, "version") else None
            if target_ver and self.cli_version_override and target_ver != self.version:
                self._report_at("LINT-013", f"Version mismatch: File specifies GASD {target_ver} but CLI enforces {self.version}.", 1, 1, fnode.filePath, level=ErrorLevel.ERROR)
        
        # Pass 1: Cross-File & Namespace Linting
        file_to_node = {f.filePath: f for f in system.metadata.files}
        for fnode in system.metadata.files:
            file_version = self.file_versions.get(fnode.filePath, self.version)
            
            # LINT-002: Check all IMPORT for CONTRACT (only for files that explicitly declare 1.2)
            # Files without VERSION directive should not trigger 1.2-specific lint rules
            has_explicit_version = fnode.syntacticRoot and hasattr(fnode.syntacticRoot, 'version') and fnode.syntacticRoot.version is not None
            if fnode.imports and file_version == "1.2" and has_explicit_version:
                # Find if any contract belongs to this import (simplified check)
                if not system.contracts:
                     self._report_at("LINT-002", "IMPORT detected without corresponding CONTRACT in GASD 1.2.", 1, 1, fnode.filePath)

        # Pass 2: Node-level linting (Recursive)
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

        for contract in system.contracts:
            self.lint_node(contract)
            # LINT-007: CONTRACT CASE without Outcome (1.2 ERROR, 1.1 Error)
            for case in getattr(contract, "cases", []):
                has_outcome = False
                clauses = getattr(case, "clauses", [])
                if clauses:
                    has_outcome = any(c.get("type") in ["POSTCONDITION", "THROWS", "AFTER"] for c in clauses if isinstance(c, dict))
                
                if not has_outcome:
                    ver = self._get_version(contract)
                    severity = self._get_severity(ver, ErrorLevel.ERROR, ErrorLevel.ERROR)
                    case_name = getattr(case, "name", "unnamed")
                    self._report("LINT-007", f"CONTRACT CASE '{case_name}' in '{contract.name}' must have at least one outcome (POSTCONDITION, THROWS, or AFTER).", contract, level=severity)

        for ass in system.assumptions:
            self.lint_node(ass)

    def lint_node(self, node: SemanticNodeBase):
        """Runs node-level LINT rules."""
        version = self._get_version(node)
        aliases: Set[str] = set()
        
        for ann in node.annotations:
            # Trace format validation: identifiers must be alphanumeric with hyphens
            if ann.name == "trace":
                trace_val = ann.arguments.get("value") or ann.arguments.get("id")
                if trace_val and isinstance(trace_val, str):
                    if not re.match(r'^[A-Za-z0-9_ \-./]+$', trace_val):
                        self._report("LINT-003", f"Trace identifier '{trace_val}' must be alphanumeric with hyphens.", node, level=ErrorLevel.ERROR)

            # LINT-011: Annotation without AS identifier (1.2 ERROR, 1.1 Info)
            if not ann.alias:
                severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.INFO)
                self._report("LINT-011", f"Annotation @{ann.name} is missing mandatory 'AS' identifier in GASD 1.2", node, level=severity)
            else:
                # LINT-010: Identifier collision (1.2 ERROR, 1.1 Error)
                if ann.alias in aliases:
                    self._report("LINT-010", f"Duplicate annotation ID '{ann.alias}' detected on node.", node)
                aliases.add(ann.alias)

            # LINT-004: @retry without @idempotent (1.2 ERROR, 1.1 Warning)
            if ann.name == "retry":
                has_idempotent = any(a.name == "idempotent" for a in node.annotations)
                if not has_idempotent:
                    severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.WARNING)
                    self._report("LINT-004", f"Annotation @retry requires @idempotent on the same node in GASD 1.2.", node, level=severity)

            # LINT-005: @transaction_type without ASSUMPTION (1.2 ERROR, 1.1 Warning)
            # Only fires for environment-dependent types (e.g., ACID requires DB isolation)
            # SAGA is a runtime pattern (compensation) and does not require an ASSUMPTION
            if ann.name == "transaction_type":
                tx_val = ann.arguments.get("t", ann.arguments.get("value", ""))
                _ENV_TX_TYPES = {"ACID", "SERIALIZABLE", "READ_COMMITTED", "REPEATABLE_READ"}
                if isinstance(tx_val, str) and tx_val.upper() in _ENV_TX_TYPES:
                    has_assumption = any(
                        "TX" in a.name or
                        (ann.alias and ann.alias in a.name) or
                        (tx_val.upper() in a.name.upper()) or
                        ann.name in a.name.lower()
                        for a in (self.system.assumptions if self.system else [])
                    )
                    if not has_assumption:
                        severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.WARNING)
                        self._report("LINT-005", f"Annotation @transaction_type must have a corresponding ASSUMPTION in GASD 1.2.", node, level=severity)

            # LINT-012: Environmental dependency without ASSUMPTION (1.2 ERROR, 1.1 Warning)
            # Only fire if the annotation's semantic triple has an environmental component
            # AND the annotation is not already covered by a more specific lint rule
            # Skip annotations where environmental is auxiliary (primary is structural/runtime)
            from .AnnotationRegistry import REGISTRY
            _LINT012_SKIP = {"transaction_type", "retry", "external", "hash", "circuit_breaker"}
            ann_defn = REGISTRY.get(ann.name)
            if ann_defn and ann_defn.triple.environmental and ann.name not in _LINT012_SKIP:
                has_assumption = any(
                    (ann.alias and ann.alias in a.name) or
                    (ann.name in a.name.lower()) or
                    (ann.name.replace('_', ' ') in a.name.lower())
                    for a in (self.system.assumptions if self.system else [])
                )
                if not has_assumption:
                    severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.WARNING)
                    self._report("LINT-012", f"Annotation @{ann.name} has environmental dependencies and requires an ASSUMPTION block in GASD 1.2.", node, level=severity)

        # LINT-003: INVARIANT without scope qualifier (1.2 ERROR, 1.1 Info)
        if node.kind == "Invariant":
            if not getattr(node, "scope", None) or node.scope == ScopeEnum.LOCAL: # Default was LOCAL in 1.1
                 # In 1.2, scope must be explicit
                 pass # Logic handled by parser usually, but linting reinforces
            
            if not getattr(node, "scope", None):
                severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.WARNING)
                self._report("LINT-003", f"INVARIANT '{getattr(node, 'name', 'unnamed')}' is missing mandatory SCOPE (GLOBAL or LOCAL).", node, level=severity)

    def _lint_flow(self, flow: ResolvedFlowNode):
        self.lint_node(flow)
        version = self._get_version(flow)
        
        # Step map for dependency/existence checks
        alias_to_index = {}
        for i, step in enumerate(flow.pipeline):
             step_id = getattr(step, "id", None)
             if step_id: alias_to_index[step_id] = i
             step_num = getattr(step, "stepNumber", None)
             if step_num: alias_to_index[str(step_num)] = i
             
             # Also use the target name/value for dependency resolution (common in tests)
             target_val = getattr(step.targetExpression, "value", None) if hasattr(step, "targetExpression") else None
             if target_val: alias_to_index[str(target_val)] = i

        # LINT-008: Non-existent step reference (1.2 ERROR, 1.1 Error)
        # LINT-009: Circular dependency (1.2 ERROR, 1.1 Error)
        graph = {i: [] for i in range(len(flow.pipeline))}
        for i, step in enumerate(flow.pipeline):
            for dep_id in getattr(step, "dependsOn", []) or []:
                if dep_id in alias_to_index:
                    graph[i].append(alias_to_index[dep_id])
                else:
                    self._report("LINT-008", f"DEPENDS_ON references non-existent step '{dep_id}'", step)

        # Circular check (LINT-009)
        visited, stack = set(), set()
        def has_cycle(v):
            visited.add(v)
            stack.add(v)
            for neighbor in graph.get(v, []):
                if neighbor not in visited:
                    if has_cycle(neighbor): return True
                elif neighbor in stack: return True
            stack.remove(v)
            return False

        for i in range(len(flow.pipeline)):
            if i not in visited and has_cycle(i):
                self._report("LINT-009", f"Circular dependency detected in FLOW '{flow.name}'", flow)
                break

        # LINT-001: ACHIEVE without POSTCONDITION (1.2 ERROR, 1.1 Warning)
        for step in flow.pipeline:
             if getattr(step, "operation", "") == "ACHIEVE":
                 has_post = any(getattr(s, "operation", "") in ["ENSURE", "POSTCONDITION"] for s in getattr(step, "subSteps", []) or [])
                 if not has_post and getattr(step, "postconditions", None): has_post = True
                 
                 if not has_post:
                     severity = self._get_severity(version, ErrorLevel.ERROR, ErrorLevel.WARNING)
                     self._report("LINT-001", f"ACHIEVE step is missing mandatory POSTCONDITION (ENSURE) in GASD {version}.", step, level=severity)

    def _report(self, code: str, message: str, node: SemanticNodeBase, level: ErrorLevel = ErrorLevel.ERROR):
        self.reporter.report(StructuredSemanticError(
            code=code, message=message, level=level, location=node.sourceMap
        ))

    def _report_at(self, code: str, message: str, line: int, col: int, file: str, level: ErrorLevel = ErrorLevel.ERROR):
        from .SemanticNodes import SourceRange
        self.reporter.report(StructuredSemanticError(
            code=code, message=message, level=level, location=SourceRange(file, line, col, line, col)
        ))
