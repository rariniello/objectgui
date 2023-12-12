import os
import sys

scriptPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(os.path.join(scriptPath, '..', '..')))

from objectgui.core.node import Node
from objectgui.core.fileNode import FileNode
import pytest


# Monkey patch the gui part of the Node class for testing
def _createEditForm(self):
    pass

Node._createEditForm = _createEditForm


# Normally I wouldn't test internal functions, but all the public function
# `save` does is call this and write it to disk and we don't want to test writing to disk
def test_buildSaveDict_encodes_fileNode_and_children():
    """ Tests that _saveNode encodes a node and its children into a dictionary. """
    root = FileNode(name="root")
    child1 = Node("child1")
    child1.parent = root
    child2 = Node("child2")
    child2.parent = root

    data = root._buildSaveDict()

    expected = {
        'attributes': {'name': 'root', 'filename': None},
        'class': 'FileNode',
        'children': [
            {
                'attributes': {'name': 'child1'},
                'class': 'Node',
                'children': []
            },
            {
                'attributes': {'name': 'child2'},
                'class': 'Node',
                'children': []
            }
        ]
    }
    assert data == expected


def test_buildSaveDict_encodes_tree_with_multiple_levels():
    """ Tests that _saveNode correctly encodes a tree with multiple levels of nesting. """
    root = FileNode(name="root")
    child1 = Node("child1")
    child1.parent = root
    child2 = Node("child2")
    child2.parent = root
    child1_1 = Node("child1_1")
    child1_1.parent = child1
    child1_2 = Node("child1_2")
    child1_2.parent = child1

    data = root._buildSaveDict()

    expected = {
        'attributes': {'name': 'root', 'filename': None},
        'class': 'FileNode',
        'children': [
            {
                'attributes': {'name': 'child1'},
                'class': 'Node',
                'children': [
                    {
                        'attributes': {'name': 'child1_1'},
                        'class': 'Node',
                        'children': []
                    },
                    {
                        'attributes': {'name': 'child1_2'},
                        'class': 'Node',
                        'children': []
                    }
                ]
            },
            {
                'attributes': {'name': 'child2'},
                'class': 'Node',
                'children': []
            }
        ]
    }
    assert data == expected


def test_buildSaveDict_encodes_tree_with_ownFile():
    """ Tests that _saveNode correctly encodes a tree with a child with ownFile. """
    root = FileNode(name="root")
    child1 = Node(name="child1")
    child1.ownFile = True
    child1.parent = root
    child2 = Node("child2")
    child2.parent = root
    child1_1 = Node("child1_1")
    child1_1.parent = child1
    child1_2 = Node("child1_2")
    child1_2.parent = child1

    data = root._buildSaveDict()

    expected = {
        'attributes': {'name': 'root', 'filename': None},
        'class': 'FileNode',
        'children': [
            {
                'attributes': {'name': 'child1'},
                'class': 'Node',
                'children': []
            },
            {
                'attributes': {'name': 'child2'},
                'class': 'Node',
                'children': []
            }
        ]
    }
    assert data == expected


# TODO create some basic json files and test the load function
# Create tests for the same three scenarios as above

def test_load_fileNode_and_children():
    """ Tests that load decodes json and generate the contained node with children. """


def test_load_tree_with_multiple_levels():
    """ Tests that load decodes json and generate the contained node with children."""


def test_load_tree_with_ownFile():
    """ Tests that load decodes and creates a tree from multiple json files."""


# TODO create tests that save a tree to file and recreate it by loading from file