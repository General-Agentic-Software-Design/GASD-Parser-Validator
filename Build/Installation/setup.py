from setuptools import setup, find_packages

setup(
    name="gasd_parser",
    version="2.1.5",
    packages=["gasd_parser"] + ["gasd_parser." + p for p in find_packages(where="../../Impl")],
    package_dir={"gasd_parser": "../../Impl"},
    install_requires=[
        "antlr4-python3-runtime==4.13.1",
    ],
    entry_points={
        "console_scripts": [
            "gasd_parser=gasd_parser.cli:main",
        ],
    },
)
