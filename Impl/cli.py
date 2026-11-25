import argparse
import json
import os
import sys
import datetime

from .ast.ASTGenerator import ASTGenerator
from .ast.ASTExporter import ASTExporter
from .parser.ParseTreeAPI import ParseTreeAPI, SourceCapture
from .validation.ValidationPipeline import ValidationPipeline
from .errors.ErrorReporter import ErrorReporter, IOErrorData
from .semantic.ASTProvenance import (
    CONTENT_HASH_KEY,
    CONTENT_VERSION_KEY,
    content_fingerprints,
    report_fingerprints,
)
from .semantic.SemanticASTExporter import SemanticASTExporter
from .semantic.VersionResolver import VersionResolver
try:
    from . import __version__, __build_time__
except ImportError:
    __version__ = "2.1.10"
    __build_time__ = "DEVELOPMENT-BUILD"

def main():
    # === Phase 1: Setup and Versioning ===
    parser = argparse.ArgumentParser(prog="gasd_parser", description="GASD-Parser: Validation for Agentic Software Design.")
    parser.add_argument("path", nargs='*', help="Path to .gasd file and/or directory for recursive traversal.")
    parser.add_argument("--json", action="store_true", help="Write AST JSON to stdout and the JSON validation report to stderr.")
    parser.add_argument("--ast-sem", action="store_true", default=True, help="Full semantic AST validation (Default).")
    parser.add_argument("--ast-combine", action="store_true", help="Combine multiple files into a single SemanticSystem.")
    parser.add_argument("--ast-output", help="Write AST JSON exclusively to this file.")
    parser.add_argument("--gasd-ver", help="Force specific GASD version (1.1 or 1.2).")
    parser.add_argument("--no-validate", action="store_true", help="Skip semantic validation, generate AST only (Not recommended).")
    parser.add_argument("-v", "--version", action="version", version="gasd_parser " + __version__ + " (built: "+__build_time__+")")
    
    # Check for removed options (Tombstone)
    if "--ast" in sys.argv:
        print("Error: Unknown argument '--ast'. Feature removed in GASD 2.0 (unknown argument). Use '--ast-sem' for semantic AST validation.", file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    has_ast_output = args.ast_output is not None
    export_requested = args.json or has_ast_output or args.ast_combine
    semantic_export_requested = export_requested and args.ast_sem and not args.no_validate

    if not args.path and sys.stdin.isatty():
        stream = sys.stderr if args.json or has_ast_output else sys.stdout
        print(f"GASD-Parser Version: {__version__} (Build: {__build_time__})\n", file=stream)
        parser.print_help(file=stream)
        return

    target_files = []
    use_stdin = False
    for p in args.path:
        if p == "-":
            use_stdin = True
        elif os.path.isfile(p):
            target_files.append(os.path.abspath(p))
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith(".gasd"):
                        target_files.append(os.path.abspath(os.path.join(root, f)))
        elif args.json and semantic_export_requested:
            target_files.append(os.path.abspath(p))
        else:
            print(f"Error: Path not found {p}", file=sys.stderr)
            sys.exit(1)

    if not args.path and not sys.stdin.isatty():
        use_stdin = True

    if not target_files and not use_stdin:
        print("Error: No .gasd files found to validate.", file=sys.stderr)
        sys.exit(1)

    # === Phase 2: Syntactic Validation and Local Analysis ===
    parser_api = ParseTreeAPI()
    source_paths = {}
    source_digests = {}
    exporter = SemanticASTExporter(source_paths)
    cwd = os.getcwd()
    reporters = {}
    valid_asts = []
    collected_asts = []
    processed_files = set()
    queue = sorted(target_files)
    if use_stdin:
        queue.append("stdin")

    while queue:
        file_path = queue.pop(0)
        if file_path in processed_files: continue
        processed_files.add(file_path)

        try:
            capture_path = file_path
            if semantic_export_requested and file_path != "stdin":
                capture_path = os.path.realpath(file_path)
            if semantic_export_requested:
                logical_path = exporter._do_relativize(capture_path, cwd)
                if not logical_path or os.path.isabs(logical_path):
                    raise ValueError("Could not establish a logical source path")
                source_paths[file_path] = logical_path

            if file_path == "stdin":
                encoding = sys.stdin.encoding or "utf-8"
                errors = sys.stdin.errors or "strict"
                buffer = getattr(sys.stdin, "buffer", None)
                data = buffer.read() if buffer is not None else sys.stdin.read().encode(encoding, errors)
                capture = SourceCapture(data)
                tree, reporter = parser_api.parse_capture(capture, file_path, encoding=encoding, errors=errors)
            else:
                capture = parser_api.read_capture(capture_path)
                tree, reporter = parser_api.parse_capture(capture, file_path)
        except Exception as e:
            if semantic_export_requested and file_path not in source_paths:
                try:
                    source_paths[file_path] = os.path.relpath(file_path, cwd).replace("\\", "/")
                except ValueError:
                    source_paths[file_path] = os.path.basename(file_path)
            reporter = ErrorReporter(file_path)
            reporter.add_io_error(IOErrorData(message=str(e), path=file_path, operation="READ"))

        reporters[file_path] = reporter

        if reporter.get_error_count() > 0:
            if not args.json:
                print(f"ERROR: {file_path} failed validation", file=sys.stderr)
                print(reporter.to_console(), file=sys.stderr)
            continue

        # AST Generation
        generator = ASTGenerator(source_file=file_path)
        ast = generator.visit(tree)

        # Semantic Validation (syntactic/local)
        if not args.no_validate:
            pipeline = ValidationPipeline()
            do_full_sem = args.ast_sem
            skip = ["ReferenceResolutionPass"] if do_full_sem else []
            semantic_errors = pipeline.validate(ast, skip_passes=skip)
            for err in semantic_errors:
                reporter.add_semantic_error(err)

        if not reporter.has_errors() and semantic_export_requested:
            previous = source_digests.setdefault(logical_path, capture.sha512)
            if previous != capture.sha512:
                reporter.add_io_error(IOErrorData(
                    message="Conflicting captured bytes for the same logical source path",
                    path=file_path, operation="READ",
                ))

        if not reporter.has_errors():
            valid_asts.append((file_path, ast))
            if args.ast_sem:
                 collected_asts.append(ast)
            
            # Recursive Discovery of Imports
            for d in ast.directives:
                if d.directiveType == "IMPORT" and d.values:
                    val_clean = d.values[0].strip('"\'\' ')
                    if val_clean.endswith(".gasd"):
                        abs_import = os.path.abspath(os.path.join(os.path.dirname(file_path), val_clean))
                        if abs_import not in processed_files and (semantic_export_requested or os.path.exists(abs_import)):
                            queue.append(abs_import)
    
    target_files = sorted(processed_files)

    # === Phase 4: Semantic AST Generation (Cross-File) ===
    semantic_system = None
    sem_pipeline = None
    if args.ast_sem and not args.no_validate and valid_asts:
        from .semantic.SemanticPipeline import SemanticPipeline
        from .semantic.SymbolTable import SemanticError as STSemanticError
        from .semantic.AnnotationResolver import SemanticError as AnnotationSemanticError
        from .validation.ValidationPipeline import SemanticError as ValidationSemanticError
        
        sem_pipeline = SemanticPipeline(validate_built_in_types=not args.no_validate)
        try:
            semantic_system = sem_pipeline.run([ast for _, ast in valid_asts], global_version=args.gasd_ver)
            sem_rep = sem_pipeline.get_reporter()
            for sem_err in sem_rep.errors:
                file_key = sem_err.location.file if sem_err.location and sem_err.location.file else "unknown"
                target_rep = reporters.get(file_key)
                if not target_rep and len(reporters) == 1:
                    target_rep = list(reporters.values())[0]
                elif not target_rep:
                    for rep in reporters.values():
                        target_rep = rep
                        break
                if target_rep:
                    target_rep.add_semantic_error(ValidationSemanticError(
                        code=sem_err.code, severity=sem_err.level.value, message=sem_err.message,
                        line=sem_err.location.startLine, column=sem_err.location.startCol,
                        endLine=sem_err.location.endLine, endColumn=sem_err.location.endCol,
                        sourceFile=file_key
                    ))
        except (STSemanticError, AnnotationSemanticError) as e:
            # Report the error to the first available reporter
            err_msg = str(e)
            if not args.json:
                print("ERROR: Semantic validation failed", file=sys.stderr)
                print(f"error[SEMANTIC]: {err_msg}", file=sys.stderr)
            loc = getattr(e, 'location', None)
            first_rep = list(reporters.values())[0] if reporters else None
            if first_rep:
                first_rep.add_semantic_error(ValidationSemanticError(
                    code='SEMANTIC', severity='ERROR', message=err_msg,
                    line=loc.startLine if loc else 1,
                    column=loc.startCol if loc else 1
                ))

    # === Phase 5: Result Reporting ===
    failure_count = 0
    success_count = 0
    warning_total = 0
    all_reports = []

    for file_path in target_files:
        reporter = reporters[file_path]
        abs_file_path = os.path.abspath(file_path)
        file_ver = sem_pipeline.file_versions.get(abs_file_path, sem_pipeline.file_versions.get(file_path, args.gasd_ver)) if sem_pipeline else args.gasd_ver
        
        has_warnings = reporter.get_warning_count() > 0
        is_failure = reporter.has_errors() or (file_ver == "1.2" and has_warnings)
        
        if is_failure:
            failure_count += 1
        else:
            success_count += 1
        
        warning_total += reporter.get_warning_count()

        if args.json:
            all_reports.append(reporter.to_dict())
        elif reporter.has_errors() or reporter.get_warning_count() > 0 or reporter.get_info_count() > 0:
            if is_failure:
                print(f"ERROR: {file_path} failed validation", file=sys.stderr)
            else:
                print(f"OK Passed (with warnings): {file_path}", file=sys.stderr)
            print(reporter.to_console(), file=sys.stderr)
        elif not has_ast_output:
            print(f"OK Passed: {file_path}", file=sys.stderr)

    # === Phase 4.5: Validation Marker Construction ===
    marker = None
    if args.ast_sem:
        # Check if we should include the marker (v1.2+ feature)
        # AC-PARSER-008-01: Only in strict 1.2+ environments
        is_v12 = (args.gasd_ver == "1.2")
        if not args.gasd_ver:
             if sem_pipeline and any(v == "1.2" for v in sem_pipeline.file_versions.values()):
                 is_v12 = True
             else:
                 is_v12 = False
        
        if is_v12:
            status = "PASSED"
            if args.no_validate:
                status = "NOT_PERFORMED"
            elif failure_count > 0:
                status = "FAILED"
            
            gasd_file_version = VersionResolver.resolve_metadata_version(
                [ast for _, ast in valid_asts],
                cli_version=args.gasd_ver
            )
            
            marker = {
                "status": status,
                "parser_version": __version__,
                "build_time": __build_time__,
                "validation_time": datetime.datetime.utcnow().isoformat() + "Z",
                "gasd_file_version": gasd_file_version
            }

    # === AST Export ===
    output_error = None
    export_fingerprints = None
    if export_requested and not failure_count:
        ast_json = None
        content_fields = None
        try:
            if semantic_system is not None:
                ast_json = exporter.to_json(semantic_system, marker=marker, sources=source_digests)
                if args.json:
                    artifact = json.loads(ast_json)
                    ast_marker = artifact.get("semantic_validate")
                    if ast_marker is not None:
                        content_fields = {
                            CONTENT_HASH_KEY: ast_marker[CONTENT_HASH_KEY],
                            CONTENT_VERSION_KEY: ast_marker[CONTENT_VERSION_KEY],
                        }
                    else:
                        content_fields = content_fingerprints(artifact)
            elif collected_asts and args.no_validate:
                ast = collected_asts if args.ast_combine or len(collected_asts) > 1 else collected_asts[0]
                ast_json = ASTExporter().to_json(ast)

            if ast_json is not None:
                ast_bytes = ast_json.encode("utf-8")
                if has_ast_output:
                    with open(args.ast_output, "wb") as out_f:
                        out_f.write(ast_bytes)
                    if not args.json:
                        print(f"Exported combined AST to {args.ast_output}", file=sys.stderr)
                else:
                    stdout_buffer = getattr(sys.stdout, "buffer", None)
                    if stdout_buffer is None:
                        sys.stdout.write(ast_json)
                        sys.stdout.flush()
                    else:
                        stdout_buffer.write(ast_bytes)
                        stdout_buffer.flush()
                if content_fields is not None:
                    export_fingerprints = report_fingerprints(ast_bytes, content_fields)
        except (OSError, ValueError) as exc:
            output_error = getattr(exc, "strerror", None) or str(exc) or type(exc).__name__

    if args.json:
        report = {
            "success": failure_count == 0 and output_error is None,
            "successCount": success_count,
            "failureCount": failure_count,
            "reports": all_reports,
        }
        if export_fingerprints is not None:
            report["semantic_validate"] = {**(marker or {}), **export_fingerprints}
        elif marker:
            report["semantic_validate"] = marker
        if output_error:
            report["outputError"] = {
                "path": args.ast_output or None,
                "message": f"Could not write AST: {output_error}",
            }
        report = exporter.relativize_dict(report, cwd)
        print(json.dumps(report, indent=2), file=sys.stderr)
    else:
        if output_error:
            print(f"Error: Could not write AST to {args.ast_output!r}: {output_error}", file=sys.stderr)
        print("\n--- Summary ---", file=sys.stderr)
        print(f"Files Validated: {len(target_files)}", file=sys.stderr)
        print(f"Pass:            {success_count}", file=sys.stderr)
        print(f"Failed:          {failure_count}", file=sys.stderr)
        print(f"Warnings:        {warning_total}", file=sys.stderr)

    sys.exit(1 if failure_count or output_error else 0)

if __name__ == "__main__":
    main()
