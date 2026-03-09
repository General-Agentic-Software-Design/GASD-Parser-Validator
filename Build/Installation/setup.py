from setuptools import setup, find_packages

setup(
    name="gasd-parser",
    version="1.1.1",
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
