import pytest
import json
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_stable_error_format():
    """RT-PARSER-005-01: Error JSON format remains stable."""
    api = ParseTreeAPI()
    content = "!" # Syntax error
    tree, errors = api.parse(content)
    
    report = json.loads(errors.to_json())
    assert "version" in report
    assert "errors" in report
    assert isinstance(report["errors"], list)
    for err in report["errors"]:
        assert "type" in err
        assert "location" in err
        assert "line" in err["location"]
        assert "column" in err["location"]
