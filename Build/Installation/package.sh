#!/bin/bash
set -e

echo "Starting packaging for Version 2.1.6..."

# 1. Run Tests and Update Metadata
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Inject current ISO-8601 UTC timestamp
BUILD_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 -c "import sys; content = open('Impl/__init__.py').read(); content = content.replace('DEVELOPMENT-BUILD', \"$BUILD_TIME\"); import re; content = re.sub(r'__build_time__ = \".*?\"', f'__build_time__ = \"$BUILD_TIME\"', content); open('Impl/__init__.py', 'w').write(content)"
echo "Build timestamp updated to: $BUILD_TIME"
python3 -m pytest -p no:asyncio -q
cd "$PROJECT_ROOT/Build/Installation"

# 2. Build Wheel
rm -rf build dist *.egg-info
touch "$PROJECT_ROOT/Impl/parser/generated/grammar/__init__.py"
python3 setup.py bdist_wheel sdist

# 3. Verify Wheel
if [ -f "dist/gasd_parser-2.1.6-py3-none-any.whl" ]; then
    echo "Wheel generated successfully: dist/gasd_parser-2.1.6-py3-none-any.whl"
else
    echo "ERROR: Wheel not found!"
    exit 1
fi

echo "phase6_final_packaging completed successfully! Ready for distribution."
