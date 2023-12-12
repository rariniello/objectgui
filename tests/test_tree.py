import os
import sys

scriptPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(os.path.join(scriptPath, '..', '..')))

from objectgui.core.tree import NodeMixin, CircularTreeError
import pytest


# Test class to make sure the NodeMixin class works as a mixin
class Node(NodeMixin):
    def __init__(self, a, k='test', **kwargs):
        self.a = a
        self.k = k
        super().__init__(**kwargs)


def test_setParent():
    """ Tests adding a child to a node. """
    node = Node(0)
    leaf = Node(1)
    leaf.parent = node
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf, "The leaf should be the child of node"
    assert not leaf.children, "The leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf.parent == node, "The node should be the parent of leaf"
    assert node.row is None, "The node is root so row should be None"
    assert leaf.row == 0, "The leaf should be at index 0 in node.children"


def test_removeParent():
    """ Tests removing the parent of a node. """
    node = Node(0)
    leaf = Node(1)
    leaf.parent = node
    del leaf.parent
    # Check the full state of the system and make sure it is correct
    assert not node.children, "The node should not have any children"
    assert not leaf.children, "The leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf.parent is None, "The leaf should not have any parents"
    assert node.row is None, "The node is root so row should be None"
    assert leaf.row is None, "The leaf is root so row should be None"


def test_addChild():
    """ Tests adding a child to a node. """
    node = Node(0)
    leaf = Node(1)
    node.children = [leaf]
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf, "The leaf should be the child of node"
    assert not leaf.children, "The leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf.parent == node, "The node should be the parent of leaf"
    assert node.row is None, "The node is root so row should be None"
    assert leaf.row == 0, "The leaf should be at index 0 in node.children"


def test_addChildren():
    """ Tests adding a list of children to a node. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node.children = [leaf1, leaf2, leaf3]
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf1, "The first leaf should be the first child of node"
    assert node.children[1] == leaf2, "The second leaf should be the second child of node"
    assert node.children[2] == leaf3, "The third leaf should be the third child of node"
    assert len(node.children) == node.numChildren() == 3, " The node should have exactly 3 children"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf1.parent == node, "The node should be the parent of the first leaf"
    assert leaf2.parent == node, "The node should be the parent of the second leaf"
    assert leaf3.parent == node, "The node should be the parent of the third leaf"
    assert node.row is None, "The node is root so row should be None"
    assert leaf1.row == 0, "The first leaf should be at index 0 in node.children"
    assert leaf2.row == 1, "The second leaf should be at index 1 in node.children"
    assert leaf3.row == 2, "The third leaf should be at index 2 in node.children"


def test_moveChild():
    """ Tests moving a child from one parent to another. """
    node1 = Node(10)
    node2 = Node(20)
    leaf = Node(1)
    leaf.parent = node1
    leaf.parent = node2
    # Check the full state of the system and make sure it is correct
    assert not node1.children, "The first node should have no children"
    assert node2.children[0] == leaf, "The leaf should be the child of the second node"
    assert not leaf.children, "The leaf should not have any children"
    assert node1.parent is None, "The first node should not have any parents"
    assert node2.parent is None, "The second node should not have any parents"
    assert leaf.parent == node2, "The second node should be the parent of the first leaf"
    assert node1.row is None, "The first node is root so row should be None"
    assert node2.row is None, "The second node is root so row should be None"
    assert leaf.row == 0, "The leaf should be at index 0 in node2.children"


def test_moveChildren():
    """ Tests moving a list of children from one parent to another. """
    node1 = Node(10)
    node2 = Node(20)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node1.children = [leaf1, leaf2, leaf3]
    node2.children = [leaf1, leaf2, leaf3]
    # Check the full state of the system and make sure it is correct
    assert not node1.children, "The first node should not have any children"
    assert node2.children[0] == leaf1, "The first leaf should be the first child of the second node"
    assert node2.children[1] == leaf2, "The second leaf should be the second child of the second node"
    assert node2.children[2] == leaf3, "The third leaf should be the third child of the second node"
    assert len(node2.children) == node2.numChildren() == 3, " The second node should have exactly 3 children"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node1.parent is None, "The first node should not have any parents"
    assert node2.parent is None, "The second node should not have any parents"
    assert leaf1.parent == node2, "The second node should be the parent of the first leaf"
    assert leaf2.parent == node2, "The second node should be the parent of the second leaf"
    assert leaf3.parent == node2, "The second node should be the parent of the third leaf"
    assert node1.row is None, "The first node is root so row should be None"
    assert node2.row is None, "The second node is root so row should be None"
    assert leaf1.row == 0, "The first leaf should be at index 0 in node2.children"
    assert leaf2.row == 1, "The second leaf should be at index 1 in node2.children"
    assert leaf3.row == 2, "The third leaf should be at index 2 in node2.children"


def test_appendChild():
    """ Test appending a child to a node that already has children. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node.children = [leaf1, leaf2]
    leaf3.parent = node
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf1, "The first leaf should be the first child of node"
    assert node.children[1] == leaf2, "The second leaf should be the second child of node"
    assert node.children[2] == leaf3, "The third leaf should be the third child of node"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf1.parent == node, "The node should be the parent of the first leaf"
    assert leaf2.parent == node, "The node should be the parent of the second leaf"
    assert leaf3.parent == node, "The node should be the parent of the third leaf"
    assert node.row is None, "The first node is root so row should be None"
    assert leaf1.row == 0, "The first leaf should be at index 0 in node.children"
    assert leaf2.row == 1, "The second leaf should be at index 1 in node.children"
    assert leaf3.row == 2, "The third leaf should be at index 2 in node.children"


def test_removeChildren():
    """ Tests removing all children from a node. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node.children = [leaf1, leaf2, leaf3]
    del node.children
    # Check the full state of the system and make sure it is correct
    assert not node.children, "The node should not have any children"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf1.parent is None, "The first leaf should not have any parents"
    assert leaf2.parent is None, "The second leaf should not have any parents"
    assert leaf3.parent is None, "The third leaf should not have any parents"
    assert node.row is None, "The first node is root so row should be None"
    assert leaf1.row is None, "The first leaf is root so row should be None"
    assert leaf2.row is None, "The second leaf is root so row should be None"
    assert leaf3.row is None, "The third leaf is root so row should be None"


def test_insertChild():
    """ Tests changing the index of a node in its parent's children list. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node.children = [leaf1, leaf2, leaf3]
    leaf3.row = 0
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf3, "The third leaf should be the first child of node"
    assert node.children[1] == leaf1, "The first leaf should be the second child of node"
    assert node.children[2] == leaf2, "The second leaf should be the third child of node"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf1.parent == node, "The node should be the parent of the first leaf"
    assert leaf2.parent == node, "The node should be the parent of the second leaf"
    assert leaf3.parent == node, "The node should be the parent of the third leaf"
    assert node.row is None, "The first node is root so row should be None"
    assert leaf1.row == 1, "The first leaf should be at index 1 in node.children"
    assert leaf2.row == 2, "The second leaf should be at index 2 in node.children"
    assert leaf3.row == 0, "The third leaf should be at index 0 in node.children"


def test_insertChildEnd():
    """ Tests changing the index of a node in its parent's children list to the last child. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    node.children = [leaf1, leaf2, leaf3]
    leaf1.row = 2
    # Check the full state of the system and make sure it is correct
    assert node.children[0] == leaf2, "The second leaf should be the first child of node"
    assert node.children[1] == leaf3, "The third leaf should be the second child of node"
    assert node.children[2] == leaf1, "The first leaf should be the third child of node"
    assert not leaf1.children, "The first leaf should not have any children"
    assert not leaf2.children, "The second leaf should not have any children"
    assert not leaf3.children, "The third leaf should not have any children"
    assert node.parent is None, "The node should not have any parents"
    assert leaf1.parent == node, "The node should be the parent of the first leaf"
    assert leaf2.parent == node, "The node should be the parent of the second leaf"
    assert leaf3.parent == node, "The node should be the parent of the third leaf"
    assert node.row is None, "The first node is root so row should be None"
    assert leaf1.row == 2, "The first leaf should be at index 2 in node.children"
    assert leaf2.row == 0, "The second leaf should be at index 0 in node.children"
    assert leaf3.row == 1, "The third leaf should be at index 1 in node.children"


def test_findRoot():
    """ Tests returning the root of a tree. """
    root = Node(0)
    node1 = Node(10)
    node2 = Node(20)
    node3 = Node(30)
    node4 = Node(40)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    leaf4 = Node(4)
    leaf5 = Node(5)
    root.children = [node1, node2]
    node1.children = [leaf1]
    node2.children = [node3, node4, leaf2]
    node3.children = [leaf3, leaf4]
    leaf5.parent = node4
    # Check that the root can be retrieved from any child node
    assert root.root == root, "The root of every node should be root"
    assert node1.root == root, "The root of every node should be root"
    assert node2.root == root, "The root of every node should be root"
    assert node3.root == root, "The root of every node should be root"
    assert node4.root == root, "The root of every node should be root"
    assert leaf1.root == root, "The root of every node should be root"
    assert leaf2.root == root, "The root of every node should be root"
    assert leaf3.root == root, "The root of every node should be root"
    assert leaf4.root == root, "The root of every node should be root"
    assert leaf5.root == root, "The root of every node should be root"


def test_nextSibling():
    """ Tests iterating through sibling nodes in a tree. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    leaf4 = Node(4)
    node.children = [leaf1, leaf2, leaf3, leaf4]
    assert leaf1.nextSibling() == leaf2, "The next sibling of the first leaf should be the second leaf"
    assert leaf2.nextSibling() == leaf3, "The next sibling of the second leaf should be the third leaf"
    assert leaf3.nextSibling() == leaf4, "The next sibling of the third leaf should be the fourth leaf"
    assert leaf4.nextSibling() == leaf1, "The next sibling of the fourth leaf should be the first leaf"


def test_iterChildren():
    """ Tests iterating through all the children of a node. """
    node = Node(0)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    leaf4 = Node(4)
    node.children = [leaf1, leaf2, leaf3, leaf4]
    leaves = []
    for i, leaf in enumerate(node):
        leaves.append(leaf)
        # Check that each iteration is correct
        if i == 0:
            assert leaf == leaf1, "Leaf should be the first leaf in the first loop iteration"
        elif i == 1:
            assert leaf == leaf2, "Leaf should be the second leaf in the second loop iteration"
        elif i == 2:
            assert leaf == leaf3, "Leaf should be the third leaf in the third loop iteration"
        elif i == 3:
            assert leaf == leaf4, "Leaf should be the fourth leaf in the fourth loop iteration"
        else:
            assert False, "The iterator should only go through the children once"
    # Check that the loop ran through the entire array
    assert len(leaves) == 4, "The iterable should have returned 4 leaves"


def test_iterChidrenLeaf():
    """ Tests iterating through the children of a leaf. """
    leaf = Node(0)
    for child in leaf:
        assert False, "Iterating through the children of a leaf should do nothing"


def test_iterSubtree():
    """ Test iterating through a subtree in a given tree. """
    root = Node(0)
    node1 = Node(10)
    node2 = Node(20)
    node3 = Node(30)
    node4 = Node(40)
    leaf1 = Node(1)
    leaf2 = Node(2)
    leaf3 = Node(3)
    leaf4 = Node(4)
    leaf5 = Node(5)
    root.children = [node1, node2]
    node1.children = [leaf1]
    node2.children = [node3, node4, leaf2]
    node3.children = [leaf3, leaf4]
    leaf5.parent = node4
    nodes = []
    for i, node in enumerate(root.iterSubTree()):
        nodes.append(node)
        if i == 0:
            assert node == root, "Root should be the first node returned"
        elif i == 1:
            assert node == node1, "Node1 should be the second node returned"
        elif i == 2:
            assert node == leaf1, "Leaf1 should be the third node returned"
        elif i == 3:
            assert node == node2, "Node2 should be the fourth node returned"
        elif i == 4:
            assert node == node3, "Node3 should be the fifth node returned"
        elif i == 5:
            assert node == leaf3, "Leaf3 should be the sixth node returned"
        elif i == 6:
            assert node == leaf4, "Leaf4 should be the seventh node returned"
        elif i == 7:
            assert node == node4, "Node4 should be the eighth node returned"
        elif i == 8:
            assert node == leaf5, "Leaf5 should be the ninthh node returned"
        elif i == 9:
            assert node == leaf2, "Leaf2 should be the tenth node returned"
        else:
            assert False, "The iterator should only go through the each element once"
    # Check that the loop ran through the entire tree
    assert len(nodes) == 10, "Traversing the tree should have returned 10 nodes"


def test_circularTreeParent():
    """ Test if a circular tree can be created. """
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node2.parent = node1
    node3.parent = node2
    caught = False
    try:
        node1.parent = node3
    except CircularTreeError:
        caught = True
    # Check that the appropriate error is thrown
    assert caught, "Creating a circular tree should have thrown a CircularTreeError exception"


def test_circularTreeChildfren():
    """ Test if a circular tree can be created. """
    node1 = Node(1)
    node2 = Node(2)
    node3 = Node(3)
    node1.children = [node2]
    node2.children = [node3]
    with pytest.raises(CircularTreeError):
        node3.children = [node1]


def test_selfParent():
    """ Test if a node can be set as its own parent. """
    node = Node(1)
    with pytest.raises(CircularTreeError):
        node.parent = node


def test_selfChild():
    """ Test if a node can be set as its own child. """
    node = Node(1)
    with pytest.raises(CircularTreeError):
        node.children = [node]
    
