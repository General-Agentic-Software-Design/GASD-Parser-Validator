from Impl.parser.ParseTreeAPI import ParseTreeAPI
api = ParseTreeAPI()
content = """NAMESPACE: "com.example.system"
IMPORT: "lib.core"
IMPORT: "lib.utils" AS Utils
CONTEXT: "Test"
TARGET: "Python3"
"""
tree, errors = api.parse(content)
print("Count:", errors.get_error_count())
print("Console Errors:", errors.to_console())
print("Syntax Errors list:", len(errors.syntax_errors))
