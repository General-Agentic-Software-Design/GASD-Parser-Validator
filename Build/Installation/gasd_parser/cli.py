import argparse
import json
import os
import sys

from .ast.ASTGenerator import ASTGenerator
from .parser.ParseTreeAPI import ParseTreeAPI
from .validation.ValidationPipeline import ValidationPipeline, SemanticError
from .errors.ErrorReporter import ErrorReporter, IOErrorData, SyntaxErrorData

def main():
    # === Phase 1: Setup and Versioning ===
    parser = argparse.ArgumentParser(prog="gasd_parser", description="GASD-Parser: Specialized validation for Agentic Software Design (GEP-6 compliant).")
    parser.add_argument("path", nargs='*', help="Path to .gasd file and/or directory for recursive traversal.")
    parser.add_argument("--json", action="store_true", help="Output validation results in JSON format.")
    parser.add_argument("--ast-sem", action="store_true", default=True, help="Full semantic AST validation (Default).")
    parser.add_argument("--ast-combine", action="store_true", help="Combine multiple files into a single SemanticSystem.")
    parser.add_argument("--ast-output", help="Optional path to export generated AST (JSON format).")
    parser.add_argument("--gasd-ver", help="Force specific GASD version (1.1 or 1.2).")
    parser.add_argument("--no-validate", action="store_true", help="Skip semantic validation, generate AST only (Not recommended).")
    parser.add_argument("-v", "--version", action="store_true", help="Show version information.")
    
    # Check for removed options (Tombstone)
    if "--ast" in sys.argv:
        print("Error: Unknown argument '--ast'. Feature removed in GASD 2.0 (unknown argument). Use '--ast-sem' for semantic AST validation.", file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if args.version:
        try:
            from . import __build_time__
        except ImportError:
            __build_time__ = "DEVELOPMENT"
        print(f"gasd_parser 2.1.0 (built: {__build_time__})")
        return

    if not args.path:
        # Check stdin
        if not sys.stdin.isatty():
             # Handle stdin...
             pass
        else:
             parser.print_help()
             return

    target_files = []
    for p in args.path:
        if os.path.isfile(p):
            target_files.append(os.path.abspath(p))
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if f.endswith(".gasd"):
                        target_files.append(os.path.abspath(os.path.join(root, f)))
        else:
            print(f"Error: Path not found {p}", file=sys.stderr)
            sys.exit(1)

    if not target_files:
        print("Error: No .gasd files found to validate.", file=sys.stderr)
        sys.exit(1)

    # === Phase 2: Syntactic Validation and Local Analysis ===
    parser_api = ParseTreeAPI()
    reporters = {}
    valid_asts = []
    collected_asts = []
    processed_files = set()
    queue = sorted(target_files)

    while queue:
        file_path = queue.pop(0)
        if file_path in processed_files: continue
        processed_files.add(file_path)

        tree = None
        try:
            tree = parser_api.parseFile(file_path)
            reporter = parser_api.reporter
        except Exception as e:
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
                        if os.path.exists(abs_import) and abs_import not in processed_files:
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
            print(f"ERROR: Semantic validation failed", file=sys.stderr)
            print(f"error[SEMANTIC]: {err_msg}", file=sys.stderr)
            first_rep = list(reporters.values())[0] if reporters else None
            if first_rep:
                first_rep.add_semantic_error(ValidationSemanticError(
                    code='SEMANTIC', severity='ERROR', message=err_msg,
                    line=1, column=1
                ))

    # === Phase 5: Result Reporting ===
    failure_count = 0
    success_count = 0
    warning_total = 0
    all_reports = []
    exit_code = 0

    for file_path in target_files:
        reporter = reporters[file_path]
        abs_file_path = os.path.abspath(file_path)
        file_ver = sem_pipeline.file_versions.get(abs_file_path, sem_pipeline.file_versions.get(file_path, args.gasd_ver)) if sem_pipeline else args.gasd_ver
        
        has_warnings = reporter.get_warning_count() > 0
        is_failure = reporter.has_errors() or (file_ver == "1.2" and has_warnings)
        
        if is_failure:
            exit_code = 1
            failure_count += 1
        else:
            success_count += 1
        
        warning_total += reporter.get_warning_count()

        if args.json:
            all_reports.append(reporter.to_json())
        else:
            if reporter.has_errors() or reporter.get_warning_count() > 0 or reporter.get_info_count() > 0:
                if is_failure:
                    print(f"ERROR: {file_path} failed validation", file=sys.stderr)
                else:
                    print(f"OK Passed (with warnings): {file_path}", file=sys.stderr)
                print(reporter.to_console(), file=sys.stderr)
            else:
                if not args.json and not args.ast_output:
                    print(f"OK Passed: {file_path}", file=sys.stderr)
                elif args.ast_output and not args.ast_combine and not args.ast_sem:
                    print(f"OK Passed: {file_path} (Exported to {args.ast_output})", file=sys.stderr)

    if args.json:
        combined = {
            "success": failure_count == 0,
            "successCount": success_count,
            "failureCount": failure_count,
            "reports": all_reports
        }
        if args.ast_sem and semantic_system and not args.ast_output:
            combined["asts"] = [semantic_system.to_dict()]
        print(json.dumps(combined, indent=2))
    
    # === AST Export ===
    export_data = None
    exporter = None
    if args.ast_sem and semantic_system:
         export_data = semantic_system
         from .semantic.SemanticASTExporter import SemanticASTExporter
         exporter = SemanticASTExporter()
    elif args.ast_combine and collected_asts:
         export_data = collected_asts
         from Impl.semantic.SemanticASTExporter import SemanticASTExporter
         exporter = SemanticASTExporter()

    if args.ast_output and failure_count == 0:
        if export_data is not None and exporter:
            combined_ast_json = exporter.to_json(export_data)
            try:
                with open(args.ast_output, "w") as out_f:
                    out_f.write(combined_ast_json)
                if not args.json:
                    print(f"Exported combined AST to {args.ast_output}", file=sys.stderr)
            except Exception as e:
                failure_count += 1
    elif not args.json and export_data is not None and args.ast_combine:
        combined_ast_json = exporter.to_json(export_data)
        print(combined_ast_json)

    if not args.json:
        print("\n--- Summary ---", file=sys.stderr)
        print(f"Files Validated: {len(target_files)}", file=sys.stderr)
        print(f"Pass:            {success_count}", file=sys.stderr)
        print(f"Failed:          {failure_count}", file=sys.stderr)
        print(f"Warnings:        {warning_total}", file=sys.stderr)

    sys.exit(1 if failure_count > 0 else 0)

if __name__ == "__main__":
    main()
