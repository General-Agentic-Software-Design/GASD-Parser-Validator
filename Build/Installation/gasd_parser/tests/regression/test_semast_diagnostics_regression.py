import pytest
import os
import subprocess
import json

def test_semast_error_location_reporting():
    """
    Test that semantic errors (SEMAST-ERR) report active line/column numbers, not 0:0.
    @trace #RT-SEMAST-012-01
    """
    # Create a temporary GASD file with a duplicate symbol
    test_file = "/tmp/error_loc_test.gasd"
    with open(test_file, "w") as f:
        f.write('CONTEXT: "Test"\nTARGET: "Any"\n\n\nTYPE UUID:\n    val: String\n')
    
    # UUID is on line 5
    
    try:
        # Run gasd-parser --ast-sem --json
        # We use the module execution to ensure we use the current Impl/ source
        cmd = ["python3", "-m", "Impl.cli", "--ast-sem", "--json", test_file]
        # Set PYTHONPATH to both the project root and the Impl folder to be safe
        env = os.environ.copy()
        env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # Parse JSON output
        output = json.loads(result.stdout)
        
        # Check if we have a semantic error with correct location
        reports = output.get("reports", [])
        assert len(reports) > 0, "No reports found in output"
        
        found_sem_err = False
        for report_str in reports:
            report = json.loads(report_str)
            for err in report.get("errors", []):
                if err.get("code") == "SEMANTIC":
                    found_sem_err = True
                    loc = err.get("location", {})
                    # Line 5 is where the second "TYPE UUID" is defined
                    line = loc.get("line")
                    assert line in [5], f"Expected line 5, got {line}"
                    break
        
        assert found_sem_err, "SEMANTIC error not found in output"
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    pytest.main([__file__])
