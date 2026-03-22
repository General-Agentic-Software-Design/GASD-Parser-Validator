import unittest
import unittest.mock
import os
import shutil
import tempfile
import sys
import json
from Impl.cli import main

class TestSemASTPathResolutionRegression(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app_dir = os.path.join(self.test_dir, "app")
        os.makedirs(self.app_dir)
        
        # Create shared_types.gasd
        self.shared_file = os.path.join(self.app_dir, "shared.gasd")
        with open(self.shared_file, "w") as f:
            f.write('CONTEXT: "Shared"\nTARGET: "Any"\nNAMESPACE: "shared"\nTYPE T1:\n  f: String\n')
            
        # Create service.gasd with relative import
        self.service_file = os.path.join(self.app_dir, "service.gasd")
        with open(self.service_file, "w") as f:
            # Using relative path that mimics the failing case: ../app/shared.gasd
            # if we are in app/service.gasd, ../app/shared.gasd is valid
            f.write('CONTEXT: "Service"\nTARGET: "Any"\nNAMESPACE: "service"\nIMPORT "../app/shared.gasd" AS Sh\nTYPE T2:\n  ref: Sh.T1\n')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_multi_file_dir_resolution(self):
        """
        Ensure no KeyError: '../app/shared.gasd' when running on the 'app' directory.
        """
        from io import StringIO
        stdout = StringIO()
        stderr = StringIO()
        
        # Setup arguments
        sys.argv = ["gasd-parser", "--ast-sem", self.app_dir]
        
        try:
            with unittest.mock.patch('sys.stdout', stdout), unittest.mock.patch('sys.stderr', stderr):
                main()
        except SystemExit as e:
            self.assertEqual(e.code, 0, f"CLI failed with exit code {e.code}: {stderr.getvalue()}")

        
        # If we got here, it passed. We can also verify the output contains "OK Passed"
        self.assertIn("OK Passed", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
