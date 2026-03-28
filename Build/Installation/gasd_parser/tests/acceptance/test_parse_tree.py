import pytest
from Impl.parser.ParseTreeAPI import ParseTreeAPI

def test_parse_tree_structure():
    """AT-PARSER-002-01: System node exists in parse tree."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Test"
TARGET: "Python3"
TYPE User:
    name: String
"""
    tree, errors = api.parse(content)
    assert tree is not None
    # gasd_file root must exist with section children
    assert tree.getChildCount() > 0
    # First section should be the CONTEXT directive
    assert tree.section(0).context_dir() is not None

def test_capability_children():
    """AT-PARSER-002-02: Capability nodes appear as children of System."""
    api = ParseTreeAPI()
    content = """CONTEXT: "ChildTest"
TARGET: "Python3"
COMPONENT Parent:
    INTERFACE:
        action() -> Boolean
"""
    tree, errors = api.parse(content)
    assert errors.get_error_count() == 0
    # Component should be a child section of the root gasd_file
    found_comp = False
    for i in range(tree.getChildCount()):
        section = tree.section(i)
        if section and section.component_def():
            found_comp = True
            comp = section.component_def()
            # Verify the component has INTERFACE keyword in a body item
            has_interface = False
            for item in comp.component_body_item():
                if item.INTERFACE_KW():
                    has_interface = True
                    break
            assert has_interface, "INTERFACE not found in component body"
            break
    assert found_comp, "Component node not found as child of root"

def test_order_preservation():
    """AT-PARSER-002-03: Parse tree preserves order of declarations."""
    api = ParseTreeAPI()
    content = """CONTEXT: "Order"
TARGET: "Python3"
TYPE A:
    id: Integer
TYPE B:
    id: Integer
"""
    tree, errors = api.parse(content)
    # The sections should appear in order A, then B
    # gasd_file -> section -> type_def
    sections = [tree.section(i) for i in range(tree.getChildCount()) if tree.section(i)]
    type_names = []
    for s in sections:
        if s.type_def():
            type_names.append(s.type_def().soft_id().getText())
    
    assert type_names == ["A", "B"], f"Expected [A, B], got {type_names}"

def test_constraint_attachment():
    """AT-PARSER-002-03: Constraints attach to correct element in parse tree."""
    api = ParseTreeAPI()
    content = """CONTEXT: "ConstraintTest"
TARGET: "Python3"
CONSTRAINT: "Global rule"
TYPE T:
    f: String
"""
    tree, errors = api.parse(content)
    # Find the constraint node
    found_constraint = False
    for i in range(tree.getChildCount()):
        section = tree.section(i)
        if section and section.constraint_stmt():
            text = section.constraint_stmt().STRING_LITERAL()[0].getText().strip('"')
            assert text == "Global rule"
            found_constraint = True
            break
    assert found_constraint, "Constraint node not found in parse tree"
