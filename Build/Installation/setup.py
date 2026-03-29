from setuptools import setup, find_packages

setup(
    name="gasd_parser",
    version="2.0.0",
    description="GASD Parser and Validator Engine v2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "antlr4-python3-runtime==4.13.2",
    ],
    entry_points={
        "console_scripts": [
            "gasd_parser=gasd_parser.cli:main",
        ],
    },
)
