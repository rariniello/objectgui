import os
import json
from objectgui.core.tree import NodeMixin
from objectgui.core.node import Node
from objectgui.core.defaultNode import DefaultNode
from objectgui.core.folderNode import FolderNode


class FileNode(Node):
    """ Class for a node on the tree that represents a file. 
    
    Contains the code to convert this node and it's sutree into json and methods
    to build a tree from json. One of these is always the root in the objectGui,
    but they can also be further down in the tree.
    """
    newInstance = 1
    defaultName = "File"
    classMapping = {
        "Node": Node.fromAttributes,
        "DefaultNode": DefaultNode.fromAttributes,
        "FolderNode": FolderNode.fromAttributes,
    }

    def __init__(self, filename=None, **kwargs):
        self.dragable = False
        self.dropable = True
        self.ownFile = True
        self.filename = filename
        super().__init__(**kwargs)
        self.addAttribute('filename')
    

    # TODO should the type hint be string or path-like?
    def save(self, filename: str):
        """ Encodes the FileNode and its subtree to json and saves the json to disk. 
        
        Args:
            filename: The filename to save the the json to.
        """
        if not os.path.exists(os.path.dirname(filename)):
            return False
        data = self._buildSaveDict()
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True


    def _buildSaveDict(self):
        """ Encodes this FileNode's subtree into a dictionary structure. 
        
        Returns:
            data: A dictionary representation of the subtree rooted at this FileNode.
        """
        data = {}
        self._saveNode(data, self)
        return data


    def _saveNode(self, data, node):
        """ Saves the information of a given node and its children in a dictionary format for saving to disk.
        
        Recursively calls itself on node's children to encode an entire tree in a dicitonary.
        If one of the child nodes is a FileNode, it is not encoded in the dictionary because
        it has its own file.

        Args:
            data: A dictionary that stores the saved information of a node and its children.
            node: An object that inherits from the Node class an represents a node in a tree.
        """
        data['attributes'] = node.createSaveData()
        data['class'] = type(node).__name__
        data['children'] = []
        if len(node.children) > 0 and (not node.ownFile or node == self):
            for child in node.children:
                childData = {}
                data['children'].append(childData)
                self._saveNode(childData, child)
        elif node.ownFile and node.filename is not None:
            node.save(node.filename)


    @classmethod
    def load(cls, filename):
        """ Constructs an FileNode from a given filename. 
        
        Args:
            filename: The path to the JSON file containing the serialized FileNode object.
        
        Returns:
            FileNode: A new FileNode object constructed from the data in the specified JSON file.
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        fileNode = cls.fromAttributes(data['attributes'])
        for child in data['children']:
            fileNode._createNode(child, fileNode)
        return fileNode


    @classmethod
    def _createNode(cls, data: dict, parent):
        """ Recursively creates a new node in a FileNode tree from a dictionary.

        Args:
            data: A dictionary representing the node to be constructed.
            parent: A reference to the new nodes parent node.
        """
        attributes = data['attributes']
        clsType = data['class']
        item = cls._createClass(clsType, attributes)
        item.parent = parent
        if item.ownFile:
            item.load(attributes['filename'])
        for child in data['children']:
            cls._createNode(child, item)


    @classmethod
    def _createClass(cls, clsType, attributes):
        """ Map the class names onto constructors.
        
        Subclasses need to implement this to correctly load data.
        """
        return cls.classMapping[clsType](attributes)
        if clsType == "Node":
            return Node.fromAttributes(attributes)
        if clsType == "DefaultNode":
            return DefaultNode.fromAttributes(attributes)
        if clsType == "FolderNode":
            return FolderNode.fromAttributes(attributes)
    
