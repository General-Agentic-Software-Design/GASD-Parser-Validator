# GASD Parser & Validator

The official, canonical parser and validator for the **General Agentic Software Design (GASD)** specification language (Version **1.2**).

Version **2.1.9** adds source provenance and two SHA-512 fingerprints to validated AST exports. Both `--json` stdout and `--ast-output` use the same AST format. The parser includes GEP-7 contract signature validation, ordered case guards in both AST exports, and a Python API for verifying observed calls.

## Project Structure

- **[Build/](Build/)**: Contains the [build plan](Build/ver-2.1/build_plan.gasd) and the standalone [installation package](Build/Installation/).
- **[Design/](Design/)**: GASD-level specifications for each parser component (100% compliant).
- **[Impl/](Impl/)**: Core implementation including grammar, AST generation, and semantic validation.
- [Impl/tests/](Impl/tests/)**: Comprehensive suite of 643+ acceptance and regression tests.
- **[Requirements/](Requirements/)**: Traceable user stories and acceptance criteria (GEP-6 aligned).
- **[Specs/](Specs/)**: Collection of valid and invalid GASD samples used for testing and demo (Includes GASD 1.2 examples).

## The Hallucination Problem & Agent Self-Verification

A core challenge in Agentic Software Engineering is **hallucination**: LLMs forgetting constraints, inventing non-existent APIs, or drifting from the original human design over long contexts.

The `gasd-parser` solves this by acting as the **inflexible source of truth**.

GASD Agents can use this parser for **self-verification loops**:

1. **Human Intent**: A human writes a high-level Design `.gasd` file.
2. **Machine Validation**: The Agent runs `gasd-parser design.gasd` to ensure the human's design is structurally sound.
3. **Agent Implementation**: The Agent breaks the design down into code or lower-level `.gasd` files.
4. **Self-Check**: Before presenting work to the human, the Agent runs `gasd-parser generated.gasd --json`.
5. **Auto-Correction**: If the parser finds semantic errors (e.g., *Duplicate Type*, *Unknown Dependency*), the Agent programmatically reads the JSON error report and corrects its own output before continuing.

By enforcing strict, language-level compliance through standard compiler design, the parser mathematically eliminates design drift and hallucinations within the architecture specifications.

## Getting Started

### Prerequisites

- Python >= 3.9
- [ANTLR4 Runtime](https://www.antlr.org/download.html) (Python 3)

### Installation (Standalone CLI)

The easiest way to use the parser is to install it as a standalone tool:

```bash
python3 -m pip install Build/Installation/dist/gasd_parser-2.1.9-py3-none-any.whl
```

To uninstall the standalone CLI:

```bash
pip3 uninstall gasd_parser
```

See the [Installation README](Build/Installation/README.md) for more details.

## Usage

### Running without Installation (Developer Mode)

If you are developing the parser and want to run it directly from the source, **set up a virtual environment first**:

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows

# 2. Install the required dependencies
pip3 install -r requirements.txt

# 3. Run the parser from the project root
python3 -m Impl.cli path/to/spec.gasd

# 4. Run the full feature demo
python3 demo.py
```

### Validate a specification (Installed)

Once installed, use the `gasd_parser` command:

```bash
# Validate a specification
gasd_parser my_spec.gasd

# Write the Semantic AST from stdout to a file
gasd_parser my_spec.gasd --json > ast.json

# Write the same AST format directly to a file and capture the validation report
gasd_parser my_spec.gasd --json --ast-output ast.json 2> parse-report.json

# Combine the Semantic ASTs for multiple input files
gasd_parser spec1.gasd spec2.gasd --ast-combine --ast-output combined.json
```

`--json` writes the AST to stdout and the JSON validation report to stderr. `--ast-output` directs the AST exclusively to the specified file. The AST has a top-level `SemanticSystem` when semantic validation runs. Separate invocations can have different generated node IDs and validation timestamps.

### AST provenance

Each validated semantic AST includes `provenance.sources`, a sorted list of the logical paths and SHA-512 digests of the exact source bytes used. The JSON report's `semantic_validate` object contains `semantic_ast_bytes_sha512` for the complete exported artifact, `semantic_ast_content_sha512` for the canonical semantic model, and `semantic_ast_content_version` for the applicable [content fingerprint rules](Requirements/ver-2.x/ver-2.1/AST-Provenance-Requirements.md#semantic-content-fingerprint-version-1).

### Verifying an observed call

Pass a contract from the AST export to `gasd_parser.semantic.ContractVerifier`. Call `select_eligible_cases(contract, arguments)` with the raw arguments before argument validation or invocation, then call `verify_outcome(cases, arguments, observation)`. For recorded calls, `verify_call(contract, arguments, observation)` performs both checks.

Create a `CallObservation` with completion mode `normal`, `success`, `failure`, or `exception`. Use `success` and `failure` for the two `Result<T>` variants and `VOID` for the unit value. Quoted evidence is keyed by case name and zero-based postcondition index. The report status is `verified`, `unverified`, `violation`, or `verification_error`.

## Development

### Setup Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Running Tests

The project maintains 100% traceability to user stories. Run the test suite:

```bash
python3 -m pytest Impl/tests -v
```

### Build Plan Traceability

The project follows a 6-phase build plan defined in [Build_plan.gasd](Build/ver-2.1/build_plan.gasd):

1. **Design** maps requirements to GASD design files.
2. **Validation** defines the scenarios for acceptance, regression, and rejection.
3. **Testing** turns the scenarios into executable tests.
4. **Implementation** delivers the parser and validator changes.
5. **Quality gate** runs the full test suite and bundled examples.
6. **Packaging** builds and verifies the wheel and source distribution.

## License

MIT
