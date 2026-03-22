import os
import re
import datetime
from setuptools import setup, find_packages

init_path = os.path.join("gasd_parser", "__init__.py")
if os.path.exists(init_path):
    with open(init_path, "r") as f:
        content = f.read()
    
    current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    content = re.sub(r'__build_time__\s*=\s*".*"', f'__build_time__ = "{current_time}"', content)
    
    with open(init_path, "w") as f:
        f.write(content)

setup(
    name="gasd-parser",
    version="1.4.0",
    author="GASD Team",
    description="Official GASD 1.1 Parser and Validator",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "antlr4-python3-runtime==4.13.2",
    ],
    entry_points={
        "console_scripts": [
            "gasd-parser=gasd_parser.cli:main",
        ],
    },
    python_requires=">=3.8",
)
