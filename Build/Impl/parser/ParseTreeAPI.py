from antlr4 import InputStream, CommonTokenStream
from .GASDIndentationLexer import GASDIndentationLexer
from .generated.grammar.GASDParser import GASDParser
from ..errors.ErrorReporter import ErrorReporter, GASDErrorListener

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
        stream = InputStream(source)
        lexer = GASDIndentationLexer(stream)
        tokens = CommonTokenStream(lexer)
        tokens.fill()
        
        parser = GASDParser(tokens)

        self.reporter = ErrorReporter(source_file=source_file)
        error_listener = GASDErrorListener(self.reporter)
        
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        tree = parser.gasd_file()
        
        return tree, self.reporter

    def parseFile(self, file_path: str):
        """Parses a GASD file from disk."""
        with open(file_path, 'r') as f:
            content = f.read()
        return self.parse(content, source_file=file_path)[0]

    def getErrors(self):
        return self.reporter.syntax_errors + self.reporter.semantic_errors if self.reporter else []

    def isValid(self) -> bool:
        return not self.reporter.has_errors() if self.reporter else True
