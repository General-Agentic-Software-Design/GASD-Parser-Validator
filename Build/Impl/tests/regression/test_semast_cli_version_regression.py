import subprocess
import os
import pytest

def test_cli_version_build_time_not_development(tmp_path):
    """
    Ensure that when run as a package (simulated), the build time is not 'DEVELOPMENT'.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    impl_path = os.path.join(project_root, "Impl")
    
    # Create a temporary directory and symlink Impl to gasd_parser
    pkg_dir = tmp_path / "pkg_anchor"
    pkg_dir.mkdir()
    os.symlink(impl_path, pkg_dir / "gasd_parser")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(pkg_dir)
    
    result = subprocess.run(
        ["python3", "-m", "gasd_parser", "--version"],
        env=env,
        capture_output=True,
        text=True
    )
    
    output = result.stdout.strip() or result.stderr.strip()
    assert "gasd_parser" in output
    assert "(built: " in output
    assert "DEVELOPMENT" not in output
    # Verify it looks like an ISO-8601-ish timestamp (contains 'T' and 'Z')
    assert "T" in output and "Z" in output
