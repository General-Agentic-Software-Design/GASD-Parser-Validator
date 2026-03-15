import pytest
from Impl.semantic.SemanticNodes import SemanticNodeBase, ResolvedAnnotation, ScopeEnum, SourceRange
from Impl.semantic.AnnotationResolver import AnnotationResolver, SemanticError

class DummyASTAnnotationArg:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class DummyASTAnnotation:
    def __init__(self, name, arguments=None):
        self.name = name
        self.arguments = arguments or []


def test_semast_annotation_override():
    resolver = AnnotationResolver()
    
    # TYPE node has @sensitive(level='low')
    type_node = SemanticNodeBase("Type", SourceRange("", 0, 0, 0, 0))
    type_node.annotations = [ResolvedAnnotation("sensitive", ScopeEnum.TYPE, {"level": "low"})]
    
    # FIELD node has @sensitive(level='high')
    field_node = SemanticNodeBase("Field", SourceRange("", 0, 0, 0, 0))
    field_node.annotations = [ResolvedAnnotation("sensitive", ScopeEnum.FIELD, {"level": "high"})]
    
    # ENSURE "Field resolution overrides parent annotation value"
    merged = resolver.get_all_inherited(field_node, parent_node=type_node)
    
    sensitive_ann = next((a for a in merged if a.name == "sensitive"), None)
    assert sensitive_ann is not None
    assert sensitive_ann.arguments["level"] == "high"


def test_semast_annotation_resolution():
    resolver = AnnotationResolver()
    
    syn_ann = DummyASTAnnotation("secure", [DummyASTAnnotationArg("role", '"admin"')])
    
    # ENSURE "Syntactic text transforms into typed ResolvedAnnotation"
    resolved = resolver.resolve([syn_ann], ScopeEnum.FLOW)
    
    assert len(resolved) == 1
    assert resolved[0].name == "secure"
    assert resolved[0].scope == ScopeEnum.FLOW
    assert resolved[0].arguments["role"] == "admin"


def test_semast_annotation_validation():
    resolver = AnnotationResolver()
    
    syn_ann = DummyASTAnnotation("trace", [DummyASTAnnotationArg("value", "123")])
    
    # ENSURE "Validation rejects argument mismatch based on annotation schema"
    with pytest.raises(SemanticError, match="expects a string argument"):
        resolver.resolve([syn_ann], ScopeEnum.FLOW)


def test_semast_annotation_hierarchy():
    resolver = AnnotationResolver()
    
    comp_node = SemanticNodeBase("Component", SourceRange("", 0, 0, 0, 0))
    comp_node.annotations = [ResolvedAnnotation("deprecated", ScopeEnum.COMPONENT, {})]
    
    flow_node = SemanticNodeBase("Flow", SourceRange("", 0, 0, 0, 0))
    flow_node.annotations = []
    
    # ENSURE "get() method identifies @deprecated when analyzing any FLOW inside COMPONENT"
    ann = resolver.get(flow_node, "deprecated", parent_node=comp_node)
    
    assert ann is not None
    assert ann.name == "deprecated"


def test_semast_annotation_propagation():
    resolver = AnnotationResolver()
    
    type_node = SemanticNodeBase("Type", SourceRange("", 0, 0, 0, 0))
    type_node.annotations = [ResolvedAnnotation("secure", ScopeEnum.TYPE, {})]
    
    field_node = SemanticNodeBase("Field", SourceRange("", 0, 0, 0, 0))
    field_node.annotations = []
    
    # ENSURE "FIELD successfully inherits @secure behavior"
    merged = resolver.get_all_inherited(field_node, parent_node=type_node)
    
    secure_ann = next((a for a in merged if a.name == "secure"), None)
    assert secure_ann is not None


def test_semast_annotation_regression_unknown():
    resolver = AnnotationResolver()
    syn_ann = DummyASTAnnotation("unknown_custom_tag", [])
    
    # ENSURE "Gracefully stored as untyped annotation rather than crashing"
    resolved = resolver.resolve([syn_ann], ScopeEnum.GLOBAL)
    
    assert len(resolved) == 1
    assert resolved[0].name == "unknown_custom_tag"
