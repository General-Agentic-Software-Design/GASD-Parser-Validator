from pathlib import Path
from runpy import run_path

from setuptools import find_packages, setup


here = Path(__file__).resolve().parent
package_path = Path("src/gasd_parser")
if not (here / package_path / "__init__.py").is_file():
    package_path = Path("../../Impl")

source = here / package_path
version = run_path(str(source / "__init__.py"))["__version__"]
subpackages = find_packages(where=str(source), exclude=("tests", "tests.*"))

setup(
    name="gasd_parser",
    version=version,
    packages=["gasd_parser", *(f"gasd_parser.{package}" for package in subpackages)],
    package_dir={"gasd_parser": package_path.as_posix()},
    python_requires=">=3.9",
    install_requires=["antlr4-python3-runtime==4.13.1"],
    entry_points={"console_scripts": ["gasd_parser=gasd_parser.cli:main"]},
)
