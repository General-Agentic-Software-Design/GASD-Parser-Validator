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



class ValidationPipeline:
    def __init__(self):
        self.passes = []

    def validate(self, ast: GASDFile, skip_passes: Optional[List[str]] = None) -> List[SemanticError]:
        from .passes.DuplicateNamesPass import DuplicateNamesPass
        from .passes.RequiredSectionsPass import RequiredSectionsPass
        from .passes.ReferenceResolutionPass import ReferenceResolutionPass
        from .passes.LocationEnrichmentPass import LocationEnrichmentPass
        
        all_possible_passes = [
            DuplicateNamesPass(),
            RequiredSectionsPass(),
            ReferenceResolutionPass(),
            LocationEnrichmentPass()
        ]
        
        self.passes = [p for p in all_possible_passes if p.name not in (skip_passes or [])]
        
        all_errors = []
        for vpass in self.passes:
            all_errors.extend(vpass.validate(ast))
        return all_errors

