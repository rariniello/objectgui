import os
import sys

scriptPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(os.path.join(scriptPath, '..', '..')))

from objectgui.core.node import Node
import pytest


# Monkey patch the gui part of the Node class for testing
def _createEditForm(self):
    pass

Node._createEditForm = _createEditForm


def test_creating_node_fromAttributes():
    """ Tests creating a node from an attributes dictionary, very simple for the base class. """
    obj = Node.fromAttributes({'name': 'Test'})
    assert obj.name == 'Test'


def test_creating_subclass_fromAttributes():
    """ Tests creating a node from an attributes dictionary, very simple for the base class. """
    class CustomNode(Node):
        def __init__(self, x, y, **kwargs):
            self.x = x
            self.y = y
            super().__init__(**kwargs)
    obj = CustomNode.fromAttributes({
        'name': 'Test',
        'x': 1,
        'y': 2
        })
    assert obj.x == 1
    assert obj.y == 2
    assert obj.name == 'Test'


def test_addAttribute_default_getter_and_setter():
    """ Tests adding an attribute using the default getter and setter. """
    obj = Node("Test")
    obj.addAttribute('x')
    obj.x = 1
    assert obj.getAttributes() == {'name': 'Test', 'x': 1}
    obj.updateAttributes({'x': 2})
    assert obj.x == 2
    assert obj.getAttributes() == {'name': 'Test', 'x': 2}


def test_addAttribute_custom_getter_and_setter():
    """ Tests adding an attribute using a custom getter and setter. """
    class CustomNode(Node):
        def __init__(self):
            self.x = 1
            super().__init__("Test")
        def get_x(self):
            return self.x * 2
        def set_x(self, value):
            self.x = value * 2
    obj = CustomNode()
    obj.addAttribute('x', obj.get_x, obj.set_x)
    assert obj.getAttributes() == {'name': 'Test', 'x': 2}
    obj.updateAttributes({'x': 1})
    assert obj.x == 2
    assert obj.getAttributes() == {'name': 'Test', 'x': 4}


def test_addAttribute_lambda_getter_and_setter():
    """ Tests adding an attribute using lambdas for getters and setters. """
    obj = Node("Test")
    obj.addAttribute("x", lambda: obj.x.upper(), lambda x: setattr(obj, "x", x.lower()))
    obj.x = "hello"
    assert obj.getAttributes() == {'name': 'Test', 'x': "HELLO"}
    obj.updateAttributes({'x': "WoRlD"})
    assert obj.x == "world"
    assert obj.getAttributes() == {'name': 'Test', 'x': "WORLD"}


def test_addAttribute_invalid_name():
    """ Tests that addAttributes throws an error when an invalid name is passed. """
    obj = Node("Test")
    obj.x = None
    with pytest.raises(TypeError):
        obj.addAttribute(123)


def test_addAttribute_invalid_getter():
    """ Tests that addAttributes throws an error when an invalid getter is passed. """
    obj = Node("Test")
    obj.x = None
    with pytest.raises(TypeError):
        obj.addAttribute("x", 123)


def test_addAttribute_with_invalid_setter():
    """ Tests that addAttributes throws an error when an invalid setter is passed. """
    obj = Node("Test")
    obj.x = None
    with pytest.raises(TypeError):
        obj.addAttribute("x", lambda: 1, 123)


def test_updateAttributes_sets_attributes_correctly():
    """ Tests that update attributes sets the values of the attributes from a dictionary. """
    obj = Node("Test")
    obj.addAttribute('attr1')
    obj.addAttribute('attr2')
    obj.updateAttributes({'attr1': 1, 'attr2': 2})
    assert obj.attr1 == 1
    assert obj.attr2 == 2


def test_updateAttributes_with_invalid_attributes_raises_exception():
    """ Tests that update attributes will fail if not given a valid dictionary. """
    obj = Node("Test")
    obj.addAttribute('attr1')
    with pytest.raises(KeyError):
        obj.updateAttributes({'attr2': 2})


def test_updateAttributes_with_non_dict_arguments_raises_exception():
    """ Tests that update attributes will fail if not given a dictionary. """
    obj = Node("Test")
    obj.addAttribute('attr1')
    with pytest.raises(AttributeError):
        obj.updateAttributes('invalid argument')


def test_cacheAttributes_saves_attributes_to_cache():
    """ Tests that update attributes will fail if not given a dictionary. """
    node = Node("Test")
    node.addAttribute('attr1')
    node.addAttribute('attr2')
    node.attr1 = 1
    node.attr2 = 2
    node.cacheAttributes()
    node.attr1 = 5
    node.attr2 = 10
    node.restoreAttributesFromCache()
    assert node.attr1 == 1
    assert node.attr2 == 2


def test_cacheAttributes_overwrites_existing_cache():
    """ Tests that updating the cache will overwrite the previous cache. """
    node = Node("Test")
    node.addAttribute('attr1')
    node.attr1 = 1
    node.cacheAttributes()
    node.attr1 = 2
    node.cacheAttributes()
    node.attr1 = 3
    node.restoreAttributesFromCache()
    assert node.attr1 == 2
