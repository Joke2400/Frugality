from app.utils import TreeNode

# Create sample tree
root = TreeNode(0)
child1 = TreeNode(1)
root.add_child(child1)

child2 = TreeNode(2)
child3 = TreeNode(3)
child1.add_child(child2)
child1.add_child(child3)

child4 = TreeNode(4)
child2.add_child(child4)


def test_root_node():
    """Test root node data."""
    assert root.parent is None
    assert len(root.children) == 1
    assert root.children[0].data == 1


def test_child2():
    """Test child2 data."""
    assert child2.parent is child1
    assert child2.children[0] is child4
    assert child2.data == 2
