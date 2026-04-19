import re
from typing import Dict, List, Optional
from .SymbolTable import SemanticError
from .SemanticNodes import SystemMetadata

class DirectiveResolver:
    def __init__(self):
        self.context: Optional[str] = None
        self.targets: List[str] = []
        self.traces: set[str] = set()

    def resolve(self, directives: List[Dict[str, str]]) -> SystemMetadata:
        for directive in directives:
            kind = directive.get("kind")
            value = directive.get("value")
            scope = directive.get("scope", "Global")
            
            if kind in ["CONTEXT", "TARGET"] and scope != "Global":
                raise SemanticError(f"InvalidScope: {kind} MUST be defined at the global level.")
                
            if kind == "CONTEXT":
                stripped_value = value.strip('"\'')
                if self.context:
                    self.context = f"{self.context} | {stripped_value}"
                else:
                    self.context = stripped_value
            elif kind == "TARGET":
                self.targets.extend([t.strip('"\' ') for t in value.split(",")])
            elif kind == "TRACE":
                ids = [t.strip('"\' ') for t in value.split(",")]
                self.verify_trace_ids(ids)
                self.traces.update(ids)
                
        return SystemMetadata(
            context=self.context or "global",
            target=self.targets or ["Py"],
            trace=list(self.traces)
        )

    def verify_trace_ids(self, ids: List[str]) -> None:
        # Relaxed to allow characters used in standard examples like "SRS-111 (Title)"
        pattern = re.compile(r"^[a-zA-Z0-9\-\._ /()#]+$")
        for trace_id in ids:
            if not pattern.match(trace_id):
                raise SemanticError(f"InvalidTraceFormat: Trace ID '{trace_id}' must be alphanumeric, hyphenated, or bracketed.")

    def add_inline_traces(self, traces: List[str]) -> None:
        self.verify_trace_ids(traces)
        for trace in traces:
            self.traces.add(trace)
