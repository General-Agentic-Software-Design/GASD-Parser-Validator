import pytest
from Impl.ast.ASTNodes import GASDFile, Decision, TypeDefinition, FlowDefinition, Parameter, TypeExpression, FieldDefinition
from Impl.validation.passes.ReferenceResolutionPass import ReferenceResolutionPass

def test_regression_v010_wildcard_affects():
    """
    Test that '*' wildcard in DECISION AFFECTS does not raise V010.
    @trace #US-SEMAST-017
    """
    ast = GASDFile(
        decisions=[
            Decision(line=1, column=1, name="Infra", chosen="AWS", rationale="X", affects=["*"])
        ]
    )
    
    pass_obj = ReferenceResolutionPass()
    errors = pass_obj.validate(ast)
    
    # Ensure no V010 warnings
    v010_errors = [e for e in errors if e.code == 'V010']
    assert len(v010_errors) == 0

def test_regression_v008_local_shadowing_result():
    """
    Test that local TYPE Result shadows built-in Result generic check (V008).
    @trace #US-SEMAST-017
    """
    # Define local TYPE Result
    local_result_type = TypeDefinition(
        line=1, column=1, name="Result", 
        fields=[FieldDefinition(line=2, column=1, name="success", type=TypeExpression(baseType="Boolean"))]
    )
    
    # Define FLOW using Result (expecting it to resolve to local, thus skipping generic count check)
    flow = FlowDefinition(
        line=5, column=1, name="process", 
        parameters=[], 
        returnType=TypeExpression(baseType="Result"), # No generic args
        steps=[]
    )
    
    ast = GASDFile(
        types=[local_result_type],
        flows=[flow]
    )
    
    pass_obj = ReferenceResolutionPass()
    errors = pass_obj.validate(ast)
    
    # Ensure no v008 errors
    v008_errors = [e for e in errors if e.code == 'V008']
    assert len(v008_errors) == 0

def test_regression_v008_builtin_still_validated_if_not_shadowed():
    """
    Test that built-in Result STILL triggers V008 if NOT shadowed by a local TYPE.
    @trace #US-SEMAST-017
    """
    # Flow using Result WITHOUT local TYPE Result defined
    flow = FlowDefinition(
        line=1, column=1, name="process", 
        parameters=[], 
        returnType=TypeExpression(baseType="Result"), # 0 args, but primitive Result needs 1
        steps=[]
    )
    
    ast = GASDFile(
        types=[], # No local Result
        flows=[flow]
    )
    
    pass_obj = ReferenceResolutionPass()
    errors = pass_obj.validate(ast)
    
    # Should have V008 error
    v008_errors = [e for e in errors if e.code == 'V008' and e.severity == 'ERROR']
    assert len(v008_errors) > 0
    assert "Built-in generic 'Result' requires 1 type argument(s)" in v008_errors[0].message
