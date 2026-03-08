"""
Acceptance tests for US-PARSER-006: CLI Multiple File and Folder Processing.
"""
import pytest
import os
import tempfile
import json
from unittest.mock import patch
import sys
from io import StringIO

from Impl.cli_runner import main

def test_cli_multiple_valid_files():
    """AT-PARSER-006-01: Test parsing multiple explicit valid files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two valid GASD files
        f1_path = os.path.join(tmpdir, "valid1.gasd")
        f2_path = os.path.join(tmpdir, "valid2.gasd")
        with open(f1_path, "w") as f:
            f.write('CONTEXT: "Test1"\nTARGET: "Python"\nTYPE T1: field: String\n')
        with open(f2_path, "w") as f:
            f.write('CONTEXT: "Test2"\nTARGET: "TypeScript"\nTYPE T2: field: String\n')

        test_args = ["gasd-parser", f1_path, f2_path]
        
        stdout_capture = StringIO()
        with patch.object(sys, 'argv', test_args), \
             patch('sys.stdout', stdout_capture), \
             pytest.raises(SystemExit) as e:
            main()
            
        assert e.value.code == 0
        output = stdout_capture.getvalue()
        assert "Processed: 2 files" in output
        assert "Success:   2" in output
        assert "Failed:    0" in output

def test_cli_directory_recursive():
    """AT-PARSER-006-02: Test parsing a directory containing multiple files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a nested structure
        sub_dir = os.path.join(tmpdir, "sub", "deep")
        os.makedirs(sub_dir)
        
        f1_path = os.path.join(tmpdir, "valid.gasd")
        f2_path = os.path.join(sub_dir, "deep_valid.gasd")
        f3_path = os.path.join(tmpdir, "ignored.txt")
        
        with open(f1_path, "w") as f:
            f.write('CONTEXT: "Test1"\nTARGET: "Python"\nTYPE T1: field: String\n')
        with open(f2_path, "w") as f:
            f.write('CONTEXT: "Test2"\nTARGET: "TypeScript"\nTYPE T2: field: String\n')
        with open(f3_path, "w") as f:
            f.write("Not a gasd file")

        test_args = ["gasd-parser", tmpdir]
        
        stdout_capture = StringIO()
        with patch.object(sys, 'argv', test_args), \
             patch('sys.stdout', stdout_capture), \
             pytest.raises(SystemExit) as e:
            main()
            
        assert e.value.code == 0
        output = stdout_capture.getvalue()
        assert "Processed: 2 files" in output  # Ignored the .txt file
        assert "Success:   2" in output

def test_cli_summary_with_errors():
    """AT-PARSER-006-03: Test summary output aggregates errors accurately."""
    with tempfile.TemporaryDirectory() as tmpdir:
        f1_path = os.path.join(tmpdir, "valid.gasd")
        f2_path = os.path.join(tmpdir, "invalid.gasd")
        
        with open(f1_path, "w") as f:
            f.write('CONTEXT: "Test1"\nTARGET: "Python"\nTYPE T1: field: String\n')
        with open(f2_path, "w") as f:
            f.write('CONTEXT: "Test2"\nINVALID_SYNTAX_HERE\n')

        test_args = ["gasd-parser", tmpdir]
        
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        with patch.object(sys, 'argv', test_args), \
             patch('sys.stdout', stdout_capture), \
             patch('sys.stderr', stderr_capture), \
             pytest.raises(SystemExit) as e:
            main()
            
        assert e.value.code == 1  # Should exit 1 due to failure
        output = stdout_capture.getvalue()
        err_output = stderr_capture.getvalue()
        
        assert "Processed: 2 files" in output
        assert "Success:   1" in output
        assert "Failed:    1" in output
        assert "FAIL" in err_output
        assert "invalid.gasd" in err_output
