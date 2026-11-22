#!/bin/bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$project_root"

version="$(python3 -c 'from Impl import __version__; print(__version__)')"
echo "Packaging gasd_parser $version"
python3 -m pytest -p no:asyncio -q

stage="$(mktemp -d "${TMPDIR:-/tmp}/gasd-package.XXXXXXXX")"
trap 'rm -rf "$stage"' EXIT

python3 - "$project_root" "$stage" <<'PY'
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

project, stage = map(Path, sys.argv[1:])
metadata = project / "Impl" / "__init__.py"
build_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
contents, replacements = re.subn(
    r'^__build_time__ = ".*"$',
    f'__build_time__ = "{build_time}"',
    metadata.read_text(encoding="utf-8"),
    flags=re.MULTILINE,
)
if replacements != 1:
    raise RuntimeError("Expected a single build timestamp in Impl/__init__.py")
metadata.write_text(contents, encoding="utf-8")
print(f"Build timestamp updated to {build_time}")

shutil.copytree(
    project / "Impl",
    stage / "src" / "gasd_parser",
    ignore=shutil.ignore_patterns("tests", "__pycache__", "*.pyc", "*.jar", "*.egg-info"),
)
shutil.copy2(project / "Build" / "Installation" / "setup.py", stage / "setup.py")
shutil.copy2(project / "README.md", stage / "README.md")
shutil.copy2(project / "LICENSE", stage / "LICENSE")
PY

(
    cd "$stage"
    python3 setup.py bdist_wheel sdist
)

wheel="gasd_parser-${version}-py3-none-any.whl"
sdist="gasd_parser-${version}.tar.gz"
test -f "$stage/dist/$wheel"
test -f "$stage/dist/$sdist"

dist="$project_root/Build/Installation/dist"
mkdir -p "$dist"
cp "$stage/dist/$wheel" "$stage/dist/$sdist" "$dist/"
printf 'Built %s\n' "$dist/$wheel" "$dist/$sdist"
