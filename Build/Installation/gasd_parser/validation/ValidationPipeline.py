from dataclasses import dataclass
from typing import List, Optional
from ..ast.ASTNodes import GASDFile

@dataclass
class SemanticError:
    code: str
    severity: str # "ERROR" | "WARNING" | "INFO"
    message: str
    line: int
    column: int
    endLine: Optional[int] = None
    endColumn: Optional[int] = None
    sourceFile: Optional[str] = None
    context: Optional[str] = None
    suggestions: Optional[List[str]] = None

class ValidationPass:
    name: str = "BasePass"
    
    def validate(self, ast: GASDFile) -> List[SemanticError]:
        raise NotImplementedError("Subclasses must implement validate()")

from .passes.DuplicateNamesPass import DuplicateNamesPass
from .passes.RequiredSectionsPass import RequiredSectionsPass
from .passes.ReferenceResolutionPass import ReferenceResolutionPass
from .passes.LocationEnrichmentPass import LocationEnrichmentPass

class ValidationPipeline:
    def __init__(self):
        self.passes: List[ValidationPass] = [
            DuplicateNamesPass(),
            RequiredSectionsPass(),
            ReferenceResolutionPass(),
            LocationEnrichmentPass()
        ]

    def validate(self, ast: GASDFile) -> List[SemanticError]:
        all_errors = []
        for vpass in self.passes:
            all_errors.extend(vpass.validate(ast))
        return all_errors
