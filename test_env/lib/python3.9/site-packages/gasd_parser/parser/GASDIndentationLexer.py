from antlr4 import Token, Lexer
from .generated.grammar.GASDLexer import GASDLexer

class GASDIndentationLexer(GASDLexer):
    """
    Custom Lexer for GASD that handles Python-style significant indentation.
    It wraps the generated GASDLexer and emits synthetic INDENT and DEDENT
    tokens by monitoring the leading whitespace of each line.
    """
    def __init__(self, input_stream):
        super().__init__(input_stream)
        self.indent_stack = [0]
        self.pending_tokens = []
        self.last_token_type = 0

    def nextToken(self):
        if len(self.pending_tokens) > 0:
            token = self.pending_tokens.pop(0)
            self.last_token_type = token.type
            return token

        token = super().nextToken()

        if token.type == GASDLexer.NEWLINE:
            self.pending_tokens.append(token)

            indent_length = 0
            i = 1
            while True:
                c = self._input.LA(i)
                if c == 32:  # ' '
                    indent_length += 1
                elif c == 9:  # '\t'
                    indent_length += 4
                elif c == 10 or c == 13:  # \n or \r
                    indent_length = 0
                    break
                else:
                    break
                i += 1

            current_indent = self.indent_stack[-1]
            la_char = self._input.LA(i)

            # Check if this line is an informal header that should suppress INDENT
            # ONLY suppress INDENT for informal headers at top-level (indent from 0)
            # These are patterns like "   GASD Design:", "   ===", "   Scope:", etc.
            # Do NOT suppress for // or /// (comment lines inside indented blocks need INDENT)
            is_informal_header = False
            if current_indent == 0 and indent_length > 0:
                # Only at top level: check if this is an informal header
                if la_char == ord('*') and self._input.LA(i+1) == ord('/'):  # */
                    is_informal_header = True
                elif la_char == ord('=') and self._input.LA(i+1) == ord('=') and self._input.LA(i+2) == ord('='):  # ===
                    is_informal_header = True
                elif la_char == ord('G') and self._input.LA(i+1) == ord('A') and self._input.LA(i+2) == ord('S') and self._input.LA(i+3) == ord('D') and self._input.LA(i+4) == ord(' '):
                    is_informal_header = True
                elif la_char == ord('S') and self._input.LA(i+1) == ord('c') and self._input.LA(i+2) == ord('o') and self._input.LA(i+3) == ord('p') and self._input.LA(i+4) == ord('e') and self._input.LA(i+5) == ord(':'):
                    is_informal_header = True
                elif la_char == ord('C') and self._input.LA(i+1) == ord('o') and self._input.LA(i+2) == ord('m') and self._input.LA(i+3) == ord('p') and self._input.LA(i+4) == ord('l') and self._input.LA(i+5) == ord('i'):
                    is_informal_header = True
                elif la_char == ord('O') and self._input.LA(i+1) == ord('u') and self._input.LA(i+2) == ord('t') and self._input.LA(i+3) == ord('p') and self._input.LA(i+4) == ord('u') and self._input.LA(i+5) == ord('t'):
                    is_informal_header = True
                elif la_char == ord('S') and self._input.LA(i+1) == ord('t') and self._input.LA(i+2) == ord('a') and self._input.LA(i+3) == ord('t') and self._input.LA(i+4) == ord('u') and self._input.LA(i+5) == ord('s'):
                    is_informal_header = True
                elif la_char == ord('V') and self._input.LA(i+1) == ord('e') and self._input.LA(i+2) == ord('r') and self._input.LA(i+3) == ord('s') and self._input.LA(i+4) == ord('i') and self._input.LA(i+5) == ord('o'):
                    is_informal_header = True

            if la_char != 10 and la_char != 13 and la_char != Token.EOF:
                if indent_length > current_indent:
                    if not is_informal_header:
                        self.indent_stack.append(indent_length)
                        self.pending_tokens.append(self.create_synthetic_token(GASDLexer.INDENT, "<INDENT>", token))
                elif indent_length < current_indent:
                    self.emit_dedent_tokens_until(indent_length, token)

            return self.pending_tokens.pop(0)

        if token.type == Token.EOF:
            self.emit_dedent_tokens_until(0, token)
            self.pending_tokens.append(token)
            return self.pending_tokens.pop(0)

        self.last_token_type = token.type
        return token

    def emit_dedent_tokens_until(self, target_indent, reference_token):
        current_indent = self.indent_stack[-1]
        while current_indent > target_indent:
            self.indent_stack.pop()
            dedent_token = self.create_synthetic_token(GASDLexer.DEDENT, "<DEDENT>", reference_token)
            self.pending_tokens.append(dedent_token)
            current_indent = self.indent_stack[-1]

    def create_synthetic_token(self, token_type, text, reference_token):
        token = Token()
        token.type = token_type
        token.text = text
        token.line = reference_token.line
        token.column = reference_token.column
        token.channel = Lexer.DEFAULT_TOKEN_CHANNEL
        token.tokenIndex = -1
        token.start = -1
        token.stop = -1
        token.source = (self, self._input)
        return token
