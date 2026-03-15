from enum import Enum
from typing import List, Optional, Dict, Any
from .SemanticNodes import SourceRange

class ErrorLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

class StructuredSemanticError:
    def __init__(self, code: str, message: str, level: ErrorLevel, location: SourceRange,
                 context_path: Optional[List[str]] = None, remediation: Optional[str] = None):
        self.code = code
        self.message = message
        self.level = level
        self.location = location
        self.context_path = context_path or []
        self.remediation = remediation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level.value,
            "location": self.location.to_dict(),
            "context": self.context_path,
            "remediation": self.remediation
        }

class ErrorSummary:
    def __init__(self, errors: List[StructuredSemanticError]):
        self.errors = errors
        self.total = len(errors)
        self.warnings = sum(1 for e in errors if e.level == ErrorLevel.WARNING)
        self.critical = sum(1 for e in errors if e.level in [ErrorLevel.ERROR, ErrorLevel.FATAL])
        self.success = self.critical == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "total": self.total,
            "warnings": self.warnings,
            "critical": self.critical,
            "errors": [e.to_dict() for e in self.errors]
        }

class SemanticErrorReporter:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        # "Error reporter MUST be a singleton" 
        if not cls._instance:
            cls._instance = super(SemanticErrorReporter, cls).__new__(cls, *args, **kwargs)
            cls._instance.reset()
        return cls._instance

    def report(self, error: StructuredSemanticError) -> None:
        if not error.location:
            raise ValueError("Constraint Violation: Errors MUST include precise line/column mapping back to origin.")
        if not error.code:
            raise ValueError("Constraint Violation: Error codes MUST correspond to GASD 1.1.0 Spec sections.")
            
        self.errors.append(error)

    def get_summary(self) -> ErrorSummary:
        return ErrorSummary(self.errors)

    def reset(self) -> None:
        self.errors: List[StructuredSemanticError] = []
