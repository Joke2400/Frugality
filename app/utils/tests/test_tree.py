from app.utils import Node, depth_first_search

# Create sample tree
root = Node(0)
child1 = Node(1)
root.add_child(child1)

child2 = Node(2)
child3 = Node(3)
child1.add_child(child2)
child1.add_child(child3)

child4 = Node(4)
child2.add_child(child4)


def test_node_root():
    """Test root node data."""
    assert root.parent is None
    assert len(root.children) == 1
    assert root.children[0].data == 1


def test_child2():
    """Test child2 data."""
    assert child2.parent is child1
    assert child2.children[0] is child4

def test_bfs():
    pass