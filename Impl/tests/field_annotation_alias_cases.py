import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]


def write_design(path, annotations="@min_length(1)", version="1.2", namespace="example.hello"):
    version_line = f"VERSION {version}\n" if version else ""
    path.write_text(
        version_line
        + 'CONTEXT: "Field annotation validation"\n'
        + 'TARGET: "Go"\n'
        + f'NAMESPACE: "{namespace}"\n\n'
        + f"TYPE HelloInput:\n    name: String {annotations}\n",
        encoding="utf-8",
    )
    return path.name


def run_cli(directory, *arguments):
    return subprocess.run(
        [sys.executable, "-m", "Impl.cli", *arguments],
        cwd=directory,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
    )


def missing_aliases(report):
    return [
        (error["severity"], error["location"]["line"], error["location"]["column"])
        for error in report["errors"] if error["code"] == "LINT-011"
    ]
