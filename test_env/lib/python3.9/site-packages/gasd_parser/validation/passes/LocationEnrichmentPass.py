from typing import List
from ..ValidationPipeline import ValidationPass, SemanticError
from ...ast.ASTNodes import GASDFile

class LocationEnrichmentPass(ValidationPass):
    """
    Pass 4: Location Metadata Enrichment
    Verifies that all reported errors carry correct location data.
    @trace #AC-PARSER-004-04
    """
    name = "LocationEnrichmentPass"

    def validate(self, ast: GASDFile) -> List[SemanticError]:
        # This pass is slightly different; it would normally run *after* other passes 
        # to verify their output, or it acts as a final sanity check on the AST itself
        # ensuring every AST node has line/column info.
        
        errors = []
        
        def check_node_location(node, context_name):
            if not node: return
            if not hasattr(node, 'line') or not hasattr(node, 'column'):
                errors.append(SemanticError(
                    code='V011',
                    severity='ERROR',
                    message=f"Missing location metadata (line/column) on node.",
                    line=0, column=0,
                    context=context_name
                ))
                return
            if node.line <= 0 or node.column < 0:
                errors.append(SemanticError(
                    code='V012',
                    severity='ERROR',
                    message=f"Invalid location metadata (line={node.line}, col={node.column})",
                    line=node.line, column=node.column,
                    context=context_name
                ))
                
        for d in ast.directives: check_node_location(d, "Directive")
        for dec in ast.decisions: check_node_location(dec, dec.name)
        for t in ast.types: check_node_location(t, t.name)
        for c in ast.components: check_node_location(c, c.name)
        for f in ast.flows: check_node_location(f, f.name)
        for s in ast.strategies: check_node_location(s, s.name)
        
        return errors
