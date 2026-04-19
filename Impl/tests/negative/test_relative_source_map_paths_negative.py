import pytest
import subprocess
import os
import json
import tempfile
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def run_cli(*args, input_content=None, file_path=None, cwd=None):
    cli_args = ["python3", "-m", "Impl.cli"]
    if file_path:
        cli_args.append(file_path)
    cli_args.extend(args)

    result = subprocess.run(
        cli_args,
        capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": PROJECT_ROOT},
        cwd=cwd or PROJECT_ROOT
    )
    return result

def test_negative_no_absolute_leakage():
    """AC-PARSER-010-02 & AC-PARSER-010-06: Scans JSON to ensure NO absolute system paths leaked."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.gasd")
        with open(file_path, "w") as f:
            f.write('VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T: f: String\n')
        
        result = run_cli("--ast-sem", "--json", file_path="test.gasd", cwd=tmpdir)
        assert result.returncode == 0
        stdout = result.stdout
        
        # 1. Structural Check (Compilation Unit)
        data = json.loads(stdout)
        file_nodes = data["asts"][0]["compilationUnit"]["fileNodes"]
        for k in file_nodes.keys():
            assert not os.path.isabs(k), f"Absolute key found: {k}"
            assert k == "test.gasd"

        # 2. Comprehensive Leak Check
        # Search for absolute path patterns in the entire output string
        # Common absolute path starts: /Users, /home, /etc, C:\, D:\, /mnt
        abs_patterns = [
            r"\"/Users/", r"\"/home/", r"\"/root/", r"\"/etc/",
            r"\"[A-Z]:\\", r"\"/mnt/", r"\"/opt/"
        ]
        
        # Also check for the specific tmpdir we used
        # We escape backslashes for regex compatibility if on Windows
        escaped_tmpdir = tmpdir.replace("\\", "\\\\")
        abs_patterns.append(re.escape(tmpdir))
        abs_patterns.append(re.escape(os.path.realpath(tmpdir)))

        for pattern in abs_patterns:
            assert not re.search(pattern, stdout), f"Absolute path leakage detected with pattern: {pattern}"

def test_negative_multiple_file_relativity():
    """Verify that multiple files in different locations are all relativized correctly to one CWD."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # File 1: in CWD
        f1 = os.path.join(tmpdir, "f1.gasd")
        # File 2: in subdir
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir)
        f2 = os.path.join(subdir, "f2.gasd")
        
        content1 = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T1: f: String\n'
        content2 = 'VERSION 1.2\nCONTEXT: "Test"\nTARGET: "Py"\nTYPE T2: f: String\n'
        with open(f1, "w") as f: f.write(content1)
        with open(f2, "w") as f: f.write(content2)
        
        # Run on both
        result = run_cli("--ast-sem", "--json", "f1.gasd", "subdir/f2.gasd", cwd=tmpdir)
        assert result.returncode == 0
        
        # Output contains nodes from both files
        # We need to verify that each node has a relative path
        data = json.loads(result.stdout)
        files_found = set()
        for ast in data["asts"]:
            for ns in ast["namespaces"].values():
                for t in ns["types"].values():
                    files_found.add(t["sourceMap"]["file"])
        
        assert "f1.gasd" in files_found
        assert "subdir/f2.gasd" in files_found
        # Verify no absolute paths in the set
        for f in files_found:
            assert not os.path.isabs(f), f"Path {f} is absolute but should be relative."
