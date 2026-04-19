from typing import List
from ..ValidationPipeline import ValidationPass, SemanticError
from ...ast.ASTNodes import GASDFile

class DuplicateNamesPass(ValidationPass):
    """
    Pass 1: Duplicate Name Detection
    Ensures no two constructs of the same kind share a name.
    """
    name = "DuplicateNamesPass"

    def validate(self, ast: GASDFile) -> List[SemanticError]:
        errors = []
        
        self.check_duplicates(ast.decisions, 'Decision', errors)
        self.check_duplicates(ast.types, 'Type', errors)
        self.check_duplicates(ast.components, 'Component', errors)
        self.check_duplicates(ast.flows, 'Flow', errors)
        self.check_duplicates(ast.strategies, 'Strategy', errors)

        return errors

    def check_duplicates(self, items: List[any], kind: str, errors: List[SemanticError]):
        if not items:
            return
            
        seen = {}
        for item in items:
            if not getattr(item, 'name', None):
                continue
                
            if item.name in seen:
                errors.append(SemanticError(
                    code='V001',
                    severity='ERROR',
                    message=f"Duplicate {kind} name: '{item.name}'",
                    line=item.line,
                    column=item.column,
                    context=item.name,
                    sourceFile=item.sourceFile
                ))
            else:
                seen[item.name] = item
