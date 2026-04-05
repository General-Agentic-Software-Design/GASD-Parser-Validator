import sys
content = open("Impl/cli.py").read()
import re
# Find the start of the report loop and replace with a clean version
old_loop_pattern = r'for file_path in target_files:.*?failure_count \+= 1\s+else:\s+success_count \+= 1'
# Actually it is easier to match the whole block I want to replace
start_marker = "    # === Final Console Output for Per-file processing ==="
end_marker = "    if args.json:"
match = re.search(f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}", content, re.DOTALL)
if match:
    new_loop = """
    # === Final Console Output for Per-file processing ===
    exit_code = 0
    for file_path in target_files:
        reporter = reporters[file_path]
        file_ver = sem_pipeline.file_versions.get(file_path, args.gasd_ver) if 'sem_pipeline' in locals() else args.gasd_ver
        
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
    
    """
    new_content = content[:match.start()] + new_loop + content[match.end():]
    open("Impl/cli.py", "w").write(new_content)
    print("Successfully fixed Impl/cli.py")
else:
    print("Could not find markers in Impl/cli.py")
