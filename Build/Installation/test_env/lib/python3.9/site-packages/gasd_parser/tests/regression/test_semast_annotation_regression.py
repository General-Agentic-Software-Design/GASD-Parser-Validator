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
    type_node = SemanticNodeBase("Type", SourceRange("", 0, 0, 0, 0))
    type_node.annotations = [ResolvedAnnotation("sensitive", ScopeEnum.TYPE, {"level": "low"})]
    field_node = SemanticNodeBase("Field", SourceRange("", 0, 0, 0, 0))
    field_node.annotations = [ResolvedAnnotation("sensitive", ScopeEnum.FIELD, {"level": "high"})]
    merged = resolver.get_all_inherited(field_node, parent_node=type_node)
    sensitive = next(a for a in merged if a.name == "sensitive")
    assert sensitive.arguments["level"] == "high"

def test_semast_annotation_resolution():
    resolver = AnnotationResolver()
    syn_ann = DummyASTAnnotation("secure", [DummyASTAnnotationArg("role", '"admin"')])
    resolved = resolver.resolve([syn_ann], ScopeEnum.FLOW)
    assert len(resolved) == 1
    assert resolved[0].name == "secure"

def test_semast_annotation_validation():
    resolver = AnnotationResolver()
    syn_ann = DummyASTAnnotation("trace", [DummyASTAnnotationArg("value", "123")])
    with pytest.raises(SemanticError, match="expects a string argument"):
        resolver.resolve([syn_ann], ScopeEnum.FLOW)

def test_semast_annotation_hierarchy():
    resolver = AnnotationResolver()
    comp_node = SemanticNodeBase("Component", SourceRange("", 0, 0, 0, 0))
    comp_node.annotations = [ResolvedAnnotation("deprecated", ScopeEnum.COMPONENT, {})]
    flow_node = SemanticNodeBase("Flow", SourceRange("", 0, 0, 0, 0))
    flow_node.annotations = []
    ann = resolver.get(flow_node, "deprecated", parent_node=comp_node)
    assert ann is not None

def test_semast_annotation_propagation():
    resolver = AnnotationResolver()
    type_node = SemanticNodeBase("Type", SourceRange("", 0, 0, 0, 0))
    type_node.annotations = [ResolvedAnnotation("secure", ScopeEnum.TYPE, {})]
    field_node = SemanticNodeBase("Field", SourceRange("", 0, 0, 0, 0))
    field_node.annotations = []
    merged = resolver.get_all_inherited(field_node, parent_node=type_node)
    assert any(a.name == "secure" for a in merged)

def test_semast_annotation_regression_unknown():
    resolver = AnnotationResolver()
    syn_ann = DummyASTAnnotation("unknown_custom_tag", [])
    resolved = resolver.resolve([syn_ann], ScopeEnum.GLOBAL)
    assert len(resolved) == 1
    assert resolved[0].name == "unknown_custom_tag"
