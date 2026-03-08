"""
gasd-parser CLI — Canonical validator for GASD 1.1 specification files.

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


def main():
    parser = argparse.ArgumentParser(
        prog="gasd-parser",
        description="GASD 1.1 Parser & Validator — Canonical source of truth for GASD specification files.",
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
        version="gasd-parser 1.1.0",
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="Extract and output the AST in JSON format.",
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

    all_reports = []
    collected_asts = []
    success_count = 0
    failure_count = 0

    for file_path in target_files:
        with open(file_path, "r") as f:
            content = f.read()

        # === Phase 1: Parse ===
        api = ParseTreeAPI()
        tree, reporter = api.parse(content)
        reporter.source_file = file_path

        if reporter.get_error_count() > 0:
            if args.json:
                all_reports.append(reporter.to_json())
            else:
                print(f"FAIL  {file_path}", file=sys.stderr)
                print(reporter.to_console(), file=sys.stderr)
            failure_count += 1
            continue

        # === Phase 2: AST Generation ===
        generator = ASTGenerator(source_file=file_path)
        ast = generator.visit(tree)

        # === Phase 3: Semantic Validation ===
        semantic_errors = []
        if not args.no_validate:
            pipeline = ValidationPipeline()
            semantic_errors = pipeline.validate(ast)
            for err in semantic_errors:
                reporter.add_semantic_error(err)

        # === AST Export (Per-file) ===
        if args.ast and not reporter.has_errors():
            exporter = ASTExporter()
            if args.ast_combine:
                collected_asts.append(ast)
            else:
                ast_json = exporter.to_json(ast)
                if args.ast_output:
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
                else:
                    print(ast_json)

        # === Final Output for Per-file processing ===
        if args.json:
            all_reports.append(reporter.to_json())
            if reporter.has_errors():
                failure_count += 1
            else:
                success_count += 1
        else:
            if reporter.has_errors():
                print(f"FAIL  {file_path}", file=sys.stderr)
                print(reporter.to_console(), file=sys.stderr)
                failure_count += 1
            else:
                entity_counts = (
                    f"{len(ast.types)} types, "
                    f"{len(ast.components)} components, "
                    f"{len(ast.flows)} flows, "
                    f"{len(ast.strategies)} strategies, "
                    f"{len(ast.decisions)} decisions"
                )
                if not args.ast:
                    print(f"OK    {file_path}  ({entity_counts})")
                success_count += 1

    if args.json:
        combined = {
            "success": failure_count == 0,
            "successCount": success_count,
            "failureCount": failure_count,
            "reports": all_reports
        }
        print(json.dumps(combined, indent=2))
    
    # === AST Export (Combined) ===
    if args.ast and args.ast_combine and collected_asts:
        exporter = ASTExporter()
        combined_ast_json = exporter.to_json(collected_asts)
        if args.ast_output:
            try:
                with open(args.ast_output, "w") as out_f:
                    out_f.write(combined_ast_json)
            except Exception as e:
                print(f"Error writing combined AST to {args.ast_output}: {e}", file=sys.stderr)
                failure_count += 1
        else:
            print(combined_ast_json)

    elif len(target_files) > 1 and not args.ast:
        # @trace #AC-PARSER-006-03
        print("\n--- Summary ---")
        print(f"Processed: {len(target_files)} files")
        print(f"Success:   {success_count}")
        print(f"Failed:    {failure_count}")

    sys.exit(1 if failure_count > 0 else 0)  # @trace #AC-PARSER-006-03


if __name__ == "__main__":
    main()
