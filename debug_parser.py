import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'Build/Installation'))

from antlr4 import *
from gasd_parser.parser.generated.grammar.GASDLexer import GASDLexer
from gasd_parser.parser.generated.grammar.GASDParser import GASDParser
from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"ERROR: line {line}:{column} {msg}")

def main():
    text = """
TYPE StandardAnnotation:
    category: Enum(VALIDATION, ARCHITECTURAL)
    @range(min: Number, max: Number)
"""
    input_stream = InputStream(text)
    lexer = GASDLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = GASDParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(MyErrorListener())
    
    tree = parser.gasd_file()
    print("Parsed successfully!")
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()
