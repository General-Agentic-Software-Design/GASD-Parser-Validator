# GASD Parser & Validator

The official, canonical parser and validator for the **General Agentic Software Design (GASD)** specification language (Version **1.2**).

Version **2.1.12** reports `LINT-011` when a GASD 1.2 `TYPE` field annotation is missing its `AS` identifier. The parser verifies validated semantic AST exports against the parsed source and reports the SHA-512 digest of the delivered bytes. It includes GEP-7 contract signature validation, ordered case guards in both AST exports, and a Python API for verifying observed calls. [Release notes](Build/ver-2.1/RELEASE_NOTES_2.1.12.md)

## Project Structure

- **[Build/](Build/)**: Contains the [build plan](Build/ver-2.1/build_plan.gasd) and the standalone [installation package](Build/Installation/).
- **[Design/](Design/)**: GASD-level specifications for each parser component (100% compliant).
- **[Impl/](Impl/)**: Core implementation including grammar, AST generation, and semantic validation.
- **[Impl/tests/](Impl/tests/)**: Acceptance, regression, negative, and design tests.
- **[Requirements/](Requirements/)**: Traceable user stories and acceptance criteria (GEP-6 aligned).
- **[Specs/](Specs/)**: Collection of valid and invalid GASD samples used for testing and demo (Includes GASD 1.2 examples).

## The Hallucination Problem & Agent Self-Verification

A core challenge in Agentic Software Engineering is **hallucination**: LLMs forgetting constraints, inventing non-existent APIs, or drifting from the original human design over long contexts.

The `gasd_parser` checks authored specifications against the GASD grammar and semantic rules.

GASD Agents can use this parser for **self-verification loops**:

1. **Human Intent**: A human writes a high-level Design `.gasd` file.
2. **Machine Validation**: The Agent runs `gasd_parser design.gasd` to ensure the human's design is structurally sound.
3. **Agent Implementation**: The Agent breaks the design down into code or lower-level `.gasd` files.
4. **Self-Check**: Before presenting work to the human, the Agent runs `gasd_parser generated.gasd --json`.
5. **Auto-Correction**: If the parser finds semantic errors (e.g., *Duplicate Type*, *Unknown Dependency*), the Agent programmatically reads the JSON error report and corrects its own output before continuing.

By enforcing strict, language-level compliance through standard compiler design, the parser mathematically eliminates design drift and hallucinations within the architecture specifications.

## Getting Started

### Prerequisites

- Python >= 3.9
- [ANTLR4 Runtime](https://www.antlr.org/download.html) (Python 3)

### Installation (Standalone CLI)

The easiest way to use the parser is to install it as a standalone tool:

```bash
python3 -m pip install Build/Installation/dist/gasd_parser-2.1.12-py3-none-any.whl
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

# Write the verified AST directly to a file
gasd_parser --ast-output ast.json my_spec.gasd

# Capture the validation report as JSON
gasd_parser my_spec.gasd --json --ast-output ast.json 2> parse-report.json

# Combine the Semantic ASTs for multiple input files
gasd_parser spec1.gasd spec2.gasd --ast-combine --ast-output combined.json
```

`--json` selects a JSON validation report on stderr and sends the AST to stdout unless `--ast-output` selects a file. File export without `--json` prints a human-readable report on stderr. Validated exports have a top-level `SemanticSystem`. Separate invocations can have different generated node IDs and validation timestamps.

### AST provenance

Each validated semantic AST includes `provenance.sources`, a sorted list of the logical paths and SHA-512 digests of the exact source bytes used. The JSON report's `semantic_validate` object contains `semantic_ast_bytes_sha512` for the complete exported artifact, `semantic_ast_content_sha512` for the canonical semantic model, and `semantic_ast_content_version` for the applicable [content fingerprint rules](Requirements/ver-2.x/ver-2.1/AST-Provenance-Requirements.md#semantic-content-fingerprint-version-1).

Validated exports carry those fingerprint fields in the AST's `semantic_validate` marker for both stdout and file output. Verify the embedded byte digest by replacing its value with 128 ASCII zeros before hashing the AST bytes. Verify the report's byte digest by hashing the delivered bytes as-is. [AST provenance requirements](Requirements/ver-2.x/ver-2.1/AST-Provenance-Requirements.md#provenance-parity-across-ast-output-destinations)

### CPC AST export

Every validated semantic export resolves the entry sources and their imports and verifies the AST against occurrences captured before semantic conversion. A failed reconciliation reports the affected source occurrence and blocks publication. Use the standard `--json --ast-output` command above to capture both files. The report's root `semantic_ast_sha512` is the lowercase SHA-512 digest of the exact delivered AST bytes, including all whitespace. With `--ast-output` alone, the human-readable report includes the same digest under `semantic_ast_sha512`. `--no-validate` produces a syntax-only export without the verified inventory or digest. [CPC AST requirements](Requirements/ver-2.x/ver-2.1/GASD_Parser_AST_Requirements.md)

The AST identifies inventory revision 1 in `source_inventory_version`. Each `source_inventory` record has a `kind`, logical source `path`, one-based `line`, zero-based Unicode-character `column`, qualified `owner`, stable `identity`, and RFC 6901 JSON `pointer` to the semantic construct. The location identifies the first authored token. Annotation records also have an `alias` containing the source `AS` value or `null`. The identity encodes a compact JSON array of kind, path, line, column, and owner, with the alias appended for annotations.

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
