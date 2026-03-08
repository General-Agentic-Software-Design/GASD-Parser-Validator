import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from antlr4.error.ErrorListener import ErrorListener
from ..validation.ValidationPipeline import SemanticError

@dataclass
class SyntaxErrorData:
    type: str = "SYNTAX"
    message: str = ""
    line: int = 0
    column: int = 0
    sourceFile: str = ""
    offendingToken: Optional[str] = None
    expectedTokens: Optional[List[str]] = None
    contextSnippet: Optional[str] = None

@dataclass
class IOErrorData:
    type: str = "IO"
    message: str = ""
    path: str = ""
    operation: str = "" # "READ" or "WRITE"

class ErrorReporter:
    """
    Central error reporter that collects syntax and semantic errors.
    """
    def __init__(self, source_file: str = "unknown"):
        self.source_file = source_file
        self.syntax_errors: List[SyntaxErrorData] = []
        self.semantic_errors: List[SemanticError] = []
        self.io_errors: List[IOErrorData] = []

    def add_syntax_error(self, error: SyntaxErrorData):
        self.syntax_errors.append(error)

    def add_semantic_error(self, error: SemanticError):
        self.semantic_errors.append(error)

    def add_io_error(self, error: IOErrorData):
        self.io_errors.append(error)

    def has_errors(self) -> bool:
        return (len(self.syntax_errors) > 0 or 
                any(e.severity == "ERROR" for e in self.semantic_errors) or
                len(self.io_errors) > 0)

    def get_error_count(self) -> int:
        return len(self.syntax_errors) + sum(1 for e in self.semantic_errors if e.severity == "ERROR") + len(self.io_errors)

    def get_warning_count(self) -> int:
        return sum(1 for e in self.semantic_errors if e.severity == "WARNING")

    def to_json(self) -> str:
        """Machine-readable output format @trace #AC-PARSER-005-03"""
        report = {
            "version": "1.0.0",
            "sourceFile": self.source_file,
            "success": not self.has_errors(),
            "errorCount": self.get_error_count(),
            "warningCount": self.get_warning_count(),
            "errors": []
        }

        for err in self.syntax_errors:
            report["errors"].append({
                "type": "SYNTAX",
                "severity": "ERROR",
                "message": err.message,
                "location": {
                    "line": err.line,
                    "column": err.column
                },
                "offendingToken": err.offendingToken
            })

        for err in self.semantic_errors:
            report["errors"].append({
                "type": "SEMANTIC",
                "code": err.code,
                "severity": err.severity,
                "message": err.message,
                "location": {
                    "line": err.line,
                    "column": err.column,
                    "endLine": err.endLine,
                    "endColumn": err.endColumn
                },
                "context": err.context,
                "suggestions": err.suggestions
            })

        for err in self.io_errors:
            report["errors"].append({
                "type": "IO",
                "severity": "ERROR",
                "message": err.message,
                "path": err.path,
                "operation": err.operation
            })

        return json.dumps(report, indent=2)

    def to_console(self) -> str:
        """Human-readable console output format @trace #AC-PARSER-005-01"""
        output = []
        for err in self.syntax_errors:
            output.append(f"error[SYNTAX]: {err.message}")
            output.append(f"  --> {self.source_file}:{err.line}:{err.column}")
            if err.offendingToken:
                output.append(f"  Token: '{err.offendingToken}'")
            output.append("")

        for err in self.semantic_errors:
            tag = "error" if err.severity == "ERROR" else "warning"
            output.append(f"{tag}[SEMANTIC {err.code}]: {err.message}")
            output.append(f"  --> {self.source_file}:{err.line}:{err.column}")
            if err.context:
                output.append(f"  Context: {err.context}")
            output.append("")

        for err in self.io_errors:
            output.append(f"error[IO]: {err.message}")
            output.append(f"  Path: {err.path}")
            output.append(f"  Operation: {err.operation}")
            output.append("")
            
        return "\n".join(output)

class GASDErrorListener(ErrorListener):
    """
    Custom ANTLR error listener that captures syntax errors
    and feeds them to the ErrorReporter.
    @trace #AT-PARSER-005-01
    """
    def __init__(self, reporter: ErrorReporter):
        super().__init__()
        self.reporter = reporter

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        token_text = offendingSymbol.text if offendingSymbol else None
        
        error = SyntaxErrorData(
            message=msg,
            line=line,
            column=column,
            sourceFile=self.reporter.source_file,
            offendingToken=token_text
        )
        self.reporter.add_syntax_error(error)
