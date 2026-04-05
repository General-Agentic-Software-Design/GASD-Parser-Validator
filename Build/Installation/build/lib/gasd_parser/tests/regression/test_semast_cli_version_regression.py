import subprocess
import os
import pytest

def test_cli_version_build_time_not_development():
    """
    Ensure that when run from Build/Installation (simulated packaging), 
    the build time is not 'DEVELOPMENT'.
    """
    # Use absolute path to the project root
    project_root = "/Users/ming/Dev/GASD-Parser-Validator"
    build_path = os.path.join(project_root, "Build/Installation")
    
    # Run the version command using the Build/Installation path in PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = build_path
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--version"],
        env=env,
        capture_output=True,
        text=True
    )
    
    # Output format: gasd-parser 1.1.2 (built: 2026-03-21T17:53:08Z)
    output = result.stdout.strip()
    assert "gasd_parser" in output
    assert "(built: " in output
    assert "DEVELOPMENT" not in output
    # Verify it looks like an ISO-8601-ish timestamp (contains 'T' and 'Z')
    assert "T" in output and "Z" in output
