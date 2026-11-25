from dataclasses import dataclass, field
from hashlib import sha512
from io import BytesIO, TextIOWrapper
from pathlib import Path

from antlr4 import InputStream, CommonTokenStream
from .GASDIndentationLexer import GASDIndentationLexer
from .generated.grammar.GASDParser import GASDParser
from ..errors.ErrorReporter import ErrorReporter, GASDErrorListener


@dataclass(frozen=True)
class SourceCapture:
    data: bytes
    sha512: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "sha512", sha512(self.data).hexdigest())


class ParseTreeAPI:
    """
    Public API for parsing GASD source code.
    Follows Design/parse_tree_design.gasd
    """
    
    def __init__(self):
        self.reporter = None

    def parse(self, source: str, source_file: str = "<string>"):
        """
        Parses a GASD source string and returns (tree, reporter).
        """
        self.reporter = ErrorReporter(source_file=source_file)
        error_listener = GASDErrorListener(self.reporter)

        stream = InputStream(source)
        lexer = GASDIndentationLexer(stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        tokens = CommonTokenStream(lexer)
        tokens.fill()
        
        parser = GASDParser(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        tree = parser.gasd_file()
        
        return tree, self.reporter

    def read_capture(self, file_path: str) -> SourceCapture:
        return SourceCapture(Path(file_path).read_bytes())

    def parse_capture(self, capture: SourceCapture, source_file: str, *, encoding=None, errors=None):
        with TextIOWrapper(BytesIO(capture.data), encoding=encoding, errors=errors) as source:
            return self.parse(source.read(), source_file=source_file)

    def parseFile(self, file_path: str):
        """Parse a GASD file from a single binary capture."""
        return self.parse_capture(self.read_capture(file_path), file_path)[0]

    def getErrors(self):
        return self.reporter.syntax_errors + self.reporter.semantic_errors if self.reporter else []

    def isValid(self) -> bool:
        return not self.reporter.has_errors() if self.reporter else True
