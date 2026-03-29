import sys
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def main():
    api = ParseTreeAPI()
    file_path = "Repro/repro_bug.gasd"
    tree, reporter = api.parse(open(file_path).read())
    
    if reporter.has_errors():
        print(f"Found {len(reporter.syntax_errors)} syntax errors:")
        for err in reporter.syntax_errors:
            print(f"Line {err.line}, Col {err.column}: {err.message}")
        sys.exit(1)
    else:
        print("No syntax errors found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
