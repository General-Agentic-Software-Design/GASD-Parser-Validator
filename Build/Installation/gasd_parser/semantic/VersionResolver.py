from typing import List, Optional, Any

class VersionResolver:
    """
    Resolves the GASD version from the AST and configures version-specific rules.
    Traces: #US-V2-001, #US-V2-009
    """

    @staticmethod
    def resolve_version(ast: Any, cli_version: Optional[str] = None) -> str:
        """
        GEP-6 §10.1 / US-V2-009:
        1. If cli_version is provided, it overrides everything.
        2. Else if VERSION directive exists, use it.
        3. Default to 1.2.
        """
        if cli_version:
            return cli_version
        
        # Check for VERSION attribute first (populated by ASTGenerator)
        ast_version = getattr(ast, 'version', None)
        if ast_version:
            return ast_version.strip('"\' ')
        
        # Fallback: Check for VERSION directive in directives list (backward compatibility / robust check)
        version_directive = next((d for d in getattr(ast, 'directives', []) if d.directiveType == "VERSION"), None)
        if version_directive and version_directive.values:
            return version_directive.values[0].strip('"\' ')
        
        return "1.2"

    @staticmethod
    def is_version_12(ast: Any, cli_version: Optional[str] = None) -> bool:
        return VersionResolver.resolve_version(ast, cli_version) == "1.2"

    @staticmethod
    def validate_version_consistency(ast: Any, cli_version: Optional[str]) -> List[Any]:
        """
        LINT-013: VERSION Mismatch between CLI and file.
        Returns a list of SemanticError-like objects if a mismatch is found.
        """
        errors = []
        if not cli_version:
             return errors
             
        # Check for VERSION attribute first (populated by ASTGenerator)
        file_version = getattr(ast, 'version', None)
        
        # Fallback: Check for VERSION directive in directives list
        if not file_version:
            version_directive = next((d for d in getattr(ast, 'directives', []) if d.directiveType == "VERSION"), None)
            if version_directive and version_directive.values:
                file_version = version_directive.values[0].strip('"\' ')
        
        if file_version and file_version != cli_version:
                # We return a structured error to be handled by the reporter
                from .SemanticErrorReporter import StructuredSemanticError, ErrorLevel
                from .SemanticNodes import SourceRange
                
                # Use a dummy source range if location is missing, but preferably use what's in the AST
                loc = getattr(ast, 'sourceMap', SourceRange("unknown", 1, 0, 1, 0))
                severity = ErrorLevel.ERROR
                
                errors.append(StructuredSemanticError(
                    code="LINT-013",
                    level=severity,
                    message=f"Version mismatch: CLI specifies {cli_version} but file defines {file_version}.",
                    location=loc
                ))
        return errors
