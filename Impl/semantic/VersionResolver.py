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
        Project the declared version into Semantic AST metadata.
        If the source omits VERSION, retain the CLI or "unknown" fallback.
        """
        asts = ast if isinstance(ast, list) else [ast]
        if asts:
            declared = VersionResolver.resolve_declared_version(asts[0])
            if declared:
                return declared

        if cli_version:
            return str(cli_version).strip('"\' ')
        return "unknown"

    @staticmethod
    def validation_version(version: str) -> str:
        """Return the version of the validation rules used for this release."""
        return "1.2" if version in ("1.2.0", "1.2.1") else version

    @staticmethod
    def resolve_version(ast: Any, cli_version: Optional[str] = None) -> str:
        """Select validation rules from the CLI, the source, or the 1.2 default."""
        version = cli_version or VersionResolver.resolve_declared_version(ast) or "1.2"
        return VersionResolver.validation_version(version)

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
        
        if file_version and cli_version not in (file_version, VersionResolver.validation_version(file_version)):
                # We return a structured error to be handled by the reporter
                from .SemanticErrorReporter import StructuredSemanticError, ErrorLevel
                from .SemanticNodes import SourceRange
                
                loc = getattr(ast, "sourceMap", None)
                if loc is None:
                    file = getattr(ast, "sourceFile", "unknown")
                    line = getattr(ast, "line", 1)
                    column = getattr(ast, "column", 0)
                    loc = SourceRange(file, line, column, line, column)
                severity = ErrorLevel.ERROR
                
                errors.append(StructuredSemanticError(
                    code="LINT-013",
                    level=severity,
                    message=f"Version mismatch: CLI specifies {cli_version} but file defines {file_version}.",
                    location=loc
                ))
        return errors
