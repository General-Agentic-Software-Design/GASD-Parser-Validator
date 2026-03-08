import unittest
import subprocess
import json
import os
import shutil
import sys

class TestASTExtraction(unittest.TestCase):
    """
    Acceptance tests for US-PARSER-007: AST Extraction and JSON Output.
    """

    def setUp(self):
        self.test_dir = os.path.abspath("tmp_ast_test")
        os.makedirs(self.test_dir, exist_ok=True)
        self.sample_file = os.path.join(self.test_dir, "test.gasd")
        with open(self.sample_file, "w") as f:
            f.write('CONTEXT: "Test"\nTYPE MyType:\n    field: String\n')

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def run_parser(self, args):
        cmd = [sys.executable, "-m", "Impl"] + args
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )
        return result

    def test_ast_console_output(self):
        """AT-PARSER-007-01: Running with --ast prints JSON to console."""
        result = self.run_parser([self.sample_file, "--ast"])
        if result.returncode != 0:
            with open("debug.log", "a") as df:
                df.write(f"--- FAILED TEST ---\n")
                df.write(f"ARGS: {args}\n")
                df.write(f"STDOUT: {result.stdout}\n")
                df.write(f"STDERR: {result.stderr}\n")
        self.assertEqual(result.returncode, 0)
        # Verify JSON validity
        try:
            data = json.loads(result.stdout)
            self.assertEqual(data["kind"], "GASDFile")
            self.assertTrue(len(data["types"]) > 0)
            self.assertEqual(data["types"][0]["name"], "MyType")
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_ast_file_output(self):
        """AT-PARSER-007-02: Running with --ast-output saves to file."""
        out_json = os.path.join(self.test_dir, "out.json")
        result = self.run_parser([self.sample_file, "--ast", "--ast-output", out_json])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(out_json))
        with open(out_json, "r") as f:
            data = json.load(f)
            self.assertEqual(data["kind"], "GASDFile")

    def test_ast_no_output_on_error(self):
        """AT-PARSER-007-03: AST is NOT produced if validation fails."""
        invalid_file = os.path.join(self.test_dir, "invalid.gasd")
        with open(invalid_file, "w") as f:
            f.write('TYPE Duplicate:\n    f: String\nTYPE Duplicate:\n    f: String\n')
        
        result = self.run_parser([invalid_file, "--ast"])
        # Should fail validation
        self.assertNotEqual(result.returncode, 0)
        # Should not contain GASDFile JSON (might contain error JSON if --json was passed, but we didn't)
        self.assertNotIn('"kind": "GASDFile"', result.stdout)

    def test_ast_combine(self):
        """AT-PARSER-007-05: Running with --ast-combine produces a single JSON array."""
        file2 = os.path.join(self.test_dir, "test2.gasd")
        with open(file2, "w") as f:
            f.write('CONTEXT: "Test2"\nTYPE OtherType:\n    f: Integer\n')
        
        result = self.run_parser([self.sample_file, file2, "--ast", "--ast-combine"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_ast_multiple_files_individual(self):
        """AT-PARSER-007-04: Running with multiple files and NO --ast-combine produces separate output."""
        file2 = os.path.join(self.test_dir, "test2.gasd")
        with open(file2, "w") as f:
            f.write('CONTEXT: "Test2"\nTYPE OtherType:\n    f: Integer\n')
        
        # We'll use --ast-output to check file generation
        out_base = os.path.join(self.test_dir, "out_indiv.json")
        result = self.run_parser([self.sample_file, file2, "--ast", "--ast-output", out_base])
        self.assertEqual(result.returncode, 0)
        
        # With multiple files and no combine, it should create <out_base>.<filename>.json
        expected1 = f"{os.path.splitext(out_base)[0]}.test.json"
        expected2 = f"{os.path.splitext(out_base)[0]}.test2.json"
        
        self.assertTrue(os.path.exists(expected1), f"Missing {expected1}")
        self.assertTrue(os.path.exists(expected2), f"Missing {expected2}")

    def test_ast_invalid_output_path(self):
        """AT-PARSER-007-06: Providing an invalid path to --ast-output returns an I/O error."""
        # A directory that doesn't exist
        invalid_path = os.path.join(self.test_dir, "nonexistent_dir", "out.json")
        result = self.run_parser([self.sample_file, "--ast", "--ast-output", invalid_path])
        # It might still exit 0 if it treats it as a warning, but per AC it says "graceful with clear error messages"
        # and "return a specific I/O error message". Our CLI exits with error code if IO fail.
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error[io]", result.stderr.lower() + result.stdout.lower())

    def _verify_nodes_recursive(self, node):
        if isinstance(node, dict):
            if "kind" in node:
                self.assertIn("line", node, f"Node {node['kind']} missing line")
                self.assertIn("column", node, f"Node {node['kind']} missing column")
            for k, v in node.items():
                self._verify_nodes_recursive(v)
        elif isinstance(node, list):
            for item in node:
                self._verify_nodes_recursive(item)

    def test_ast_metadata_exhaustive(self):
        """AT-PARSER-007-07: Verify all nodes contain line/column metadata."""
        result = self.run_parser([self.sample_file, "--ast"])
        data = json.loads(result.stdout)
        self._verify_nodes_recursive(data)

    def test_ast_schema_validity(self):
        """AT-PARSER-007-08: Verify JSON output handles all expected top-level keys."""
        result = self.run_parser([self.sample_file, "--ast"])
        data = json.loads(result.stdout)
        expected_keys = ["directives", "decisions", "types", "components", "flows", "strategies", "constraints", "ensures", "matches", "questions", "approvals", "todos", "reviews"]
        for key in expected_keys:
            self.assertIn(key, data)

if __name__ == "__main__":
    import sys
    unittest.main()
