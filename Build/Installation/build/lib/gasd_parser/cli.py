"""
gasd-parser CLI — Canonical validator for GASD 1.2 specification files.

Usage:
    gasd-parser <file.gasd> [options]
    gasd-parser --help
"""

import sys
import argparse
import json
import os

from .parser.ParseTreeAPI import ParseTreeAPI
from .ast.ASTGenerator import ASTGenerator
from .ast.ASTExporter import ASTExporter
from .validation.ValidationPipeline import ValidationPipeline
from .errors.ErrorReporter import ErrorReporter, IOErrorData
from . import __version__, __build_time__


def main():

    parser = argparse.ArgumentParser(
        prog="gasd_parser",
        description="GASD 1.2 Parser & Validator — Canonical source of truth for GASD specification files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Path to one or more .gasd specification files or directories to parse and validate.",
    )  # @trace #AC-PARSER-006-01
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in machine-readable JSON format.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Run semantic validation after parsing (default: on).",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip semantic validation, only check syntax.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"gasd-parser {__version__} (built: {__build_time__})",
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="Extract and output the AST in JSON format.",
    )
    parser.add_argument(
        "--ast-sem",
        action="store_true",
        help="Extract and output the Semantic AST in JSON format.",
    )
    parser.add_argument(
        "--ast-output",
        help="Path to save the extracted AST JSON file.",
    )
    parser.add_argument(
        "--ast-combine",
        action="store_true",
        help="Combine multiple ASTs into a single JSON output.",
    )
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        sys.exit(0)

    target_files = []
    has_missing = False
    for path in args.files:
        if not os.path.exists(path):
            print(f"Error: Path not found: {path}", file=sys.stderr)
            has_missing = True
        elif os.path.isdir(path):
            # @trace #AC-PARSER-006-02
            for root, _, files in os.walk(path):
                for f in files:
                    if f.endswith(".gasd"):
                        target_files.append(os.path.join(root, f))
        else:
            target_files.append(path)

    if has_missing:
        sys.exit(1)

    if not target_files:
        print("Error: No .gasd files found to parse.", file=sys.stderr)
        sys.exit(1)

    # Sort files to ensure deterministic output order regardless of OS walk order
    target_files.sort()

    all_reports = []
    collected_asts = []
    success_count = 0
    failure_count = 0
    warning_total = 0
    
    reporters = {}
    valid_asts = []

    # === Phase 1-3: Parse & AST Generation (Recursive) ===
    reporters = {}
    valid_asts = []
    collected_asts = []
    
    processed_files = set()
    queue = list(target_files)
    
    while queue:
        file_path = os.path.abspath(queue.pop(0))
        if file_path in processed_files:
            continue
        processed_files.add(file_path)
        
        if not os.path.exists(file_path):
            # This could happen for broken imports
            continue

        with open(file_path, "r") as f:
            content = f.read()

        # Parse
        api = ParseTreeAPI()
        tree, reporter = api.parse(content)
        reporter.source_file = file_path
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

        semantic_errors = []
        if not args.no_validate:
            pipeline = ValidationPipeline()
            # Skip ReferenceResolutionPass if we're doing the full semantic pass later
            do_full_sem = args.ast_sem or (not args.ast and not args.json and not args.ast_output)
            skip = ["ReferenceResolutionPass"] if do_full_sem else []
            semantic_errors = pipeline.validate(ast, skip_passes=skip)
            for err in semantic_errors:
                reporter.add_semantic_error(err)

        if not reporter.has_errors():
            valid_asts.append((file_path, ast))
            if args.ast or args.ast_sem:
                 collected_asts.append(ast)
            
            # Recursive Discovery of Imports
            for d in ast.directives:
                if d.directiveType == "IMPORT" and d.values:
                    val_clean = d.values[0].strip('"\' ')
                    if val_clean.endswith(".gasd"):
                        abs_import = os.path.abspath(os.path.join(os.path.dirname(file_path), val_clean))
                        if os.path.exists(abs_import) and abs_import not in processed_files:
                            queue.append(abs_import)
    
    # Update target_files to include recursively discovered files for the final report
    target_files = sorted(processed_files)

    # === Phase 4: Semantic AST Generation (Cross-File) ===
    semantic_system = None
    do_full_sem = args.ast_sem or (not args.ast and not args.json and not args.ast_output)
    if do_full_sem and valid_asts:
        from .semantic.SemanticPipeline import SemanticPipeline
        from .semantic.SymbolTable import SemanticError
        from .validation.ValidationPipeline import SemanticError as ValidationSemanticError
        
        sem_pipeline = SemanticPipeline(validate_built_in_types=not args.no_validate)

        try:
            # Pass only the GASDFile ast objects
            semantic_system = sem_pipeline.run([ast for _, ast in valid_asts])
            sem_rep = sem_pipeline.get_reporter()
            for sem_err in sem_rep.errors:
                file_key = sem_err.location.file if sem_err.location and sem_err.location.file else "unknown"
                
                target_rep = reporters.get(file_key)
                if not target_rep and len(reporters) == 1:
                    target_rep = list(reporters.values())[0]
                elif not target_rep:
                    # Fallback if file mapping fails
                    for rep in reporters.values():
                        target_rep = rep
                        break
                        
                if target_rep:
                    target_rep.add_semantic_error(ValidationSemanticError(
                        code=sem_err.code,
                        severity=sem_err.level.value,
                        message=sem_err.message,
                        line=sem_err.location.startLine,
                        column=sem_err.location.startCol,
                        endLine=sem_err.location.endLine,
                        endColumn=sem_err.location.endCol,
                        sourceFile=file_key
                    ))
        except SemanticError as e:
            # Catch catastrophic pipeline failures
            loc = e.location
            file_key = loc.file if loc and loc.file else None
            
            # Find the best reporter to add the error to
            target_rep = reporters.get(file_key) if file_key else None
            if not target_rep:
                # If no specific file or reporter found, use the first one available
                target_rep = list(reporters.values())[0] if reporters else None
                
            if target_rep:
                target_rep.add_semantic_error(ValidationSemanticError(
                    code="SEMAST-ERR",
                    severity="ERROR",
                    message=str(e),
                    line=loc.startLine if loc else 0,
                    column=loc.startCol if loc else 0,
                    endLine=loc.endLine if loc else 0,
                    endColumn=loc.endCol if loc else 0,
                    sourceFile=file_key if file_key else target_rep.source_file
                ))

    # === Final Output for Per-file processing ===
    for file_path in target_files:
        reporter = reporters[file_path]
        is_failure = reporter.has_errors() or reporter.get_warning_count() > 0
        
        # Per-file AST export if not combining and not JSON output
        # ONLY DO THIS FOR syntactic AST (--ast) since Semantic AST is cross-file
        if args.ast and not args.ast_sem and not args.ast_combine and args.ast_output and not is_failure:
            export_ast = None
            for i, f_path in enumerate(target_files):
                if f_path == file_path and i < len(collected_asts):
                    export_ast = collected_asts[i]
                    break

            if export_ast:
                from .ast.ASTExporter import ASTExporter
                exporter = ASTExporter()
                ast_json = exporter.to_json(export_ast)
                
                out_path = args.ast_output
                if len(target_files) > 1:
                    base, ext = os.path.splitext(args.ast_output)
                    filename = os.path.basename(file_path).replace(".gasd", ".json")
                    out_path = f"{base}.{filename}"
                
                try:
                    with open(out_path, "w") as out_f:
                        out_f.write(ast_json)
                except Exception as e:
                    reporter.add_io_error(IOErrorData(
                        message=str(e),
                        path=out_path,
                        operation="WRITE"
                    ))

        if args.json:
            all_reports.append(reporter.to_json())
            if is_failure:
                failure_count += 1
            else:
                success_count += 1
            warning_total += reporter.get_warning_count()
        else:
            if reporter.has_errors() or reporter.get_warning_count() > 0:
                if is_failure:
                    print(f"ERROR: {file_path} failed validation", file=sys.stderr)
                else:
                    print(f"OK Passed (with warnings): {file_path}", file=sys.stderr)
                print(reporter.to_console(), file=sys.stderr)
                
                if is_failure:
                    failure_count += 1
                else:
                    success_count += 1
            else:
                if args.ast_output and not args.ast_combine and not args.ast_sem: # Only print if per-file output happened
                    print(f"OK Passed: {file_path} (Exported to {args.ast_output})", file=sys.stderr)
                else:
                    print(f"OK Passed: {file_path}", file=sys.stderr)
                success_count += 1
            
            warning_total += reporter.get_warning_count()

    if args.json:
        combined = {
            "success": failure_count == 0,
            "successCount": success_count,
            "failureCount": failure_count,
            "reports": all_reports
        }
        if args.ast_sem and semantic_system and not args.ast_output:
            # In unified mode, output the single cross-file system
            combined["asts"] = [semantic_system.to_dict()]
        elif args.ast and collected_asts and not args.ast_output:
            from .ast.ASTExporter import ASTExporter
            exporter = ASTExporter()
            combined["asts"] = [exporter._to_dict(a) for a in collected_asts if a is not None]
            
        if not args.ast_output or failure_count > 0:
            print(json.dumps(combined, indent=2))
    
    # === AST Export (Combined or Semantic) ===
    if (args.ast and args.ast_combine) or args.ast_sem:
        export_data = None
        exporter = None
        if args.ast_sem and semantic_system:
            export_data = semantic_system
            from .semantic.SemanticASTExporter import SemanticASTExporter
            exporter = SemanticASTExporter()
        elif args.ast and args.ast_combine and collected_asts:
            export_data = collected_asts
            from .ast.ASTExporter import ASTExporter
            exporter = ASTExporter()
            
        if export_data is not None and args.ast_output and failure_count == 0:
            combined_ast_json = exporter.to_json(export_data)
            try:
                with open(args.ast_output, "w") as out_f:
                    out_f.write(combined_ast_json)
                if not args.json:
                    print(f"Exported combined AST to {args.ast_output}", file=sys.stderr)
            except Exception as e:
                # Add to first reporter for lack of global error space if not json
                list(reporters.values())[0].add_io_error(IOErrorData(
                    message=str(e),
                    path=args.ast_output,
                    operation="WRITE"
                ))
                failure_count += 1
        elif not args.json and export_data is not None and args.ast_combine: # Only print if not saving to file and not producing full --json report and user explicitly requested combine
            combined_ast_json = exporter.to_json(export_data)
            print(combined_ast_json)
        else:
            # Combined AST is output via the main JSON reporting block
            pass

    if not args.json or args.ast_output:
        # Summary is always shown in non-json mode
        print("\n--- Summary ---", file=sys.stderr)
        print(f"Files Validated: {len(target_files)}", file=sys.stderr)
        print(f"Pass:            {success_count}", file=sys.stderr)
        print(f"Failed:          {failure_count}", file=sys.stderr)
        print(f"Warnings:        {warning_total}", file=sys.stderr)

    sys.exit(1 if failure_count > 0 else 0)  # @trace #AC-PARSER-006-03


if __name__ == "__main__":
    main()
