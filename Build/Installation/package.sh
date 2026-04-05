#!/usr/bin/env bash
# phase6_final_packaging script
set -e

echo "Starting phase6_final_packaging..."

cd "$(dirname "$0")"

# 1. Clean previous build states
rm -rf gasd_parser build dist gasd_parser.egg-info test_env
mkdir -p gasd_parser

# 2. Assemble artifacts locally
cp -r ../../Impl/* gasd_parser/

# Ensure generated token/grammar packages are treated correctly in wheel
if [ -f ../../Impl/parser/generated/grammar/__init__.py ]; then
    cp -r ../../Impl/parser/generated/grammar/__init__.py gasd_parser/parser/generated/grammar/
else
    echo "# Generated grammar package" > gasd_parser/parser/generated/grammar/__init__.py
fi

# 3. Inject current build time into the source package before building
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Injecting build time: $CURRENT_TIME"

# Inject into the source Impl package so dev runs also see the latest time
sed -i '' "s/__build_time__ = .*/__build_time__ = \"$CURRENT_TIME\"/g" ../../Impl/__init__.py

# For the temporary build directory (will be packaged into the wheel)
sed -i '' "s/__build_time__ = .*/__build_time__ = \"$CURRENT_TIME\"/g" gasd_parser/__init__.py

# 4. Build Wheel Configuration
echo "Building Python distributions..."
python3 setup.py sdist bdist_wheel

# 5. Clean Environment Smoke Test & Verification
echo "Setting up clean test environment..."
python3 -m venv test_env
source test_env/bin/activate
pip install wheel
pip install dist/gasd_parser-2.1.0-py3-none-any.whl

echo "Running packaging smoke tests..."

# 6. Test Build Time Updating (Verification Step)
VERSION_OUT=$(gasd_parser --version)
echo "Version Info Output: $VERSION_OUT"

if [[ "$VERSION_OUT" == *"$CURRENT_TIME"* ]]; then
    echo "✔ SUCCESS: Build time was accurately injected and executed from distribution!"
else
    echo "✖ ERROR: Build time was NOT updated in distribution!"
    echo "Expected: $CURRENT_TIME"
    echo "Found: $VERSION_OUT"
    exit 1
fi

echo "Running parse_tree_tests smoke test..."
gasd_parser --ast-sem --gasd-ver 1.1 ../../Validation/Design/parse_tree_tests.gasd

echo "phase6_final_packaging completed successfully! Ready for distribution."
