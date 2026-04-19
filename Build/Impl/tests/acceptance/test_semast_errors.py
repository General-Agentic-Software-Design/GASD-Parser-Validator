import pytest
from Impl.semantic.SemanticNodes import SourceRange
from Impl.semantic.SemanticErrorReporter import SemanticErrorReporter, StructuredSemanticError, ErrorLevel

def test_semast_error_report_and_summary():
    reporter = SemanticErrorReporter()
    reporter.reset()
    
    err1 = StructuredSemanticError(
        code="V001",
        message="Type not found",
        level=ErrorLevel.ERROR,
        location=SourceRange("file.gasd", 10, 5, 10, 15),
        context_path=["NamespaceA", "CompB"],
        remediation="Ensure type is imported."
    )
    
    err2 = StructuredSemanticError(
        code="V002",
        message="Unused variable",
        level=ErrorLevel.WARNING,
        location=SourceRange("file.gasd", 12, 1, 12, 5)
    )
    
    reporter.report(err1)
    reporter.report(err2)
    
    summary = reporter.get_summary()
    assert summary.total == 2
    assert summary.warnings == 1
    assert summary.critical == 1
    assert summary.success is False
    

def test_semast_error_mandatory_location():
    reporter = SemanticErrorReporter()
    reporter.reset()
    
    err = StructuredSemanticError(
        code="V003",
        message="Missing target",
        level=ErrorLevel.ERROR,
        location=None # Missing location
    )
    
    # "Constraint Violation: Errors MUST include precise line/column mapping back to origin."
    with pytest.raises(ValueError, match="MUST include precise line/column mapping"):
        reporter.report(err)


def test_semast_error_mandatory_code():
    reporter = SemanticErrorReporter()
    reporter.reset()
    
    err = StructuredSemanticError(
        code="", # Missing code
        message="Generic failure",
        level=ErrorLevel.ERROR,
        location=SourceRange("file", 1, 1, 1, 1)
    )
    
    # "Constraint Violation: Error codes MUST correspond to GASD 1.1.0 Spec sections."
    with pytest.raises(ValueError, match="Error codes MUST correspond to GASD"):
        reporter.report(err)


def test_semast_error_reporter_singleton():
    reporter1 = SemanticErrorReporter()
    reporter2 = SemanticErrorReporter()
    
    # "Error reporter MUST be a singleton"
    assert reporter1 is reporter2


def test_semast_error_json_serialization():
    reporter = SemanticErrorReporter()
    reporter.reset()
    
    err = StructuredSemanticError("V005", "msg", ErrorLevel.FATAL, SourceRange("f", 1,1,1,1))
    reporter.report(err)
    
    data = reporter.get_summary().to_dict()
    assert data["success"] is False
    assert data["critical"] == 1
    assert len(data["errors"]) == 1
    assert data["errors"][0]["code"] == "V005"
