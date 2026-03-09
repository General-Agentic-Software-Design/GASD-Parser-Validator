import pytest
import subprocess
import json
import os

"""
Acceptance Test for US-PARSER-007: Bulk AST Extraction
@trace #AT-PARSER-007-01, #AT-PARSER-007-02, #AT-PARSER-007-03, #AT-PARSER-007-04, #AT-PARSER-007-05, #AT-PARSER-007-06
"""

def test_cli_ast_output_console():
    """AT-PARSER-007-02: Print AST to console with --ast."""
    with open("ast_test.gasd", "w") as f: f.write('CONTEXT: "AST"\nTARGET: "Python3"\nTYPE Dummy: f: String\n')
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "ast_test.gasd", "--ast"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        assert result.returncode == 0
        # Should contain JSON structure
        ast_data = json.loads(result.stdout)
        assert ast_data["kind"] == "GASDFile"
    finally:
        os.remove("ast_test.gasd")

def test_cli_ast_output_file():
    """AT-PARSER-007-05: Save AST to specific file with --ast-output."""
    with open("ast_test.gasd", "w") as f: f.write('CONTEXT: "AST"\nTARGET: "Python3"\nTYPE Dummy: f: String\n')
    try:
        subprocess.run(["python3", "-m", "Impl.cli", "ast_test.gasd", "--ast", "--ast-output", "out.json"], capture_output=True, env={"PYTHONPATH": "."})
        assert os.path.exists("out.json")
        with open("out.json", "r") as f:
            data = json.load(f)
            assert data["kind"] == "GASDFile"
    finally:
        os.remove("ast_test.gasd")
        if os.path.exists("out.json"): os.remove("out.json")

def test_cli_ast_combine():
    """AT-PARSER-007-06: Combine multiple files into one AST JSON array."""
    with open("a1.gasd", "w") as f: f.write('CONTEXT: "A1"\nTARGET: "Python3"\nTYPE T1: f: String\n')
    with open("a2.gasd", "w") as f: f.write('CONTEXT: "A2"\nTARGET: "Python3"\nTYPE T2: f: String\n')
    try:
        result = subprocess.run(["python3", "-m", "Impl.cli", "a1.gasd", "a2.gasd", "--ast", "--ast-combine"], capture_output=True, text=True, env={"PYTHONPATH": "."})
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) == 2
    finally:
        os.remove("a1.gasd")
        os.remove("a2.gasd")
