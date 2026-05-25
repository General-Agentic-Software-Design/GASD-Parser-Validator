from typing import List, Optional, Any

class VersionResolver:
    """
    Resolves the GASD version from the AST and configures version-specific rules.
    Traces: #US-V2-001, #US-V2-009
    """

    @staticmethod
    def resolve_declared_version(ast: Any) -> Optional[str]:
        """Return the version declared by the source file, if one exists."""
        ast_version = getattr(ast, 'version', None)
        if ast_version:
            return str(ast_version).strip('"\' ')

        version_directive = next((d for d in getattr(ast, 'directives', []) if d.directiveType == "VERSION"), None)
        if version_directive and version_directive.values:
            return version_directive.values[0].strip('"\' ')

        return None

    @staticmethod
    def resolve_metadata_version(ast: Any, cli_version: Optional[str] = None) -> str:
        """
        Resolve the version value projected into Semantic AST metadata.
        Explicit CLI version overrides the source; otherwise missing source
        version is represented as the literal string "unknown".
        """
        if cli_version:
            return str(cli_version).strip('"\' ')

        asts = ast if isinstance(ast, list) else [ast]
        if asts:
            declared = VersionResolver.resolve_declared_version(asts[0])
            if declared:
                return declared

        return "unknown"

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
        
        declared = VersionResolver.resolve_declared_version(ast)
        if declared:
            return declared
        
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
             
        file_version = VersionResolver.resolve_declared_version(ast)
        
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
