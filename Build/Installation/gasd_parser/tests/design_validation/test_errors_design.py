import pytest
import json
from Impl.parser.ParseTreeAPI import ParseTreeAPI

"""
Design Validation: Error Reporting
Mapped from Validation/error_reporting_tests.gasd
"""

def test_design_error_json_output():
    """FLOW test_error_json_output"""
    api = ParseTreeAPI()
    _, errors = api.parse("INVALID")
    json_report = errors.to_json()
    data = json.loads(json_report)
    assert data["success"] is False
    assert "errors" in data
