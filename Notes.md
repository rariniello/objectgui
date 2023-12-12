# Code Structure

## Project Goals

The goal of the objectgui is to provide a simple way to build a tree based gui for manipulating objects on top of object based scientific code.

Ideally, a gui could be created for a stand alone object based simulation code by only doing the following things:

1. Create a creation/editing ui panel for each object using qt designer.
2. Create a simple interface file between the gui and each underlying object. At its simplest, this would involve connecting fields in the editing ui with getters/setters in the underlying object. It should also be able to handle more complex cases where more sophisticated gui elements are desired.
3. Create an interface file for running simulations.

## Architecture Details

The object GUI has several main pieces:

- tree.py: NodeMixin class is a mixin that turns a python class into a node of a tree.
- treeItem.py: TreeItem class is an extension of the NodeMixin class that includes features need for gui interaction and saving and loading from disk.
- objectTree.py: ObjectTree class is an extension of the TreeItem class that represented a single file, includes things like saving and loading from disk.
- treeModel.py: TreeModel class takes an instance of ObjectTree and acts as a model between the tree with the Object Tree as the root and the QTreeView that displays it.
- fileTab.py:
- mainwindow.py:

The higherarcy is setup in such a way that interfaces flow down to make development easier. First, the NodeMixin class is enirerly independent, it doesn't call any methods from the other classes. The TreeItem class is a subclass of NodeMixin and thus relies on the functionality available through the NodeMixin class, as well as relying on the EditObject widget. The TreeItem will emit signals when it does things, but it knows nothing about the FileTab or the MainWindow and never references them.

## Tree

The core code that makes all the objects that are part of the simulation code act like a tree. Built as a mixin, when mixed into another class, defines all the methods that allow the instances of the class to treated like nodes on a tree.

Interface is composed of the following:

- parent attribute: The parent node of a node, set it to move a node to a new parent and delete it to remove a node from a tree.
- children attribute: The children of a node, set it to move nodes to be children of this item and delete it to orphan all the children.
- root attribute: The root node of the tree.
- row attribute: The index of a node in its parent's children list, set it to move the node around in its parent's children array.
- isRoot method: Returns if this node is the root of the tree.
- numChildren method: Returns the number of child nodes the node has.
- nextSibling method: Returns the next sibling of a node.
- iterSubTree method: Iterates through the subtree with this node as the root in depth first order (order displayed in the gui)
- The class includes an iterater that will iterate through all children of the node.

## TreeItem

Contains the base code required to make a tree node behave as part of the gui. Several subclasses exist that define nodes with specific properties. For example, a folder node that doesn't correspond to any object in the simulation code, but is useful for organization.

Interface is composed of the following:

- addAttribute method: Adds an attribute of the underlying simulation class to the list of things that will get saved and records a way to get and set the values.
- fromAttributes method: Creates an instance of the class from a dictionary of attributes.
- update method: Updates the object from the passed dictionary of attributes.
- createSaveData: 
- createDefaultObjects
- 
