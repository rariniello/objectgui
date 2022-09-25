import os
import json
from objectgui.core.tree import NodeMixin
from objectgui.core.treeItem import TreeItem
from objectgui.core.defaultObject import DefaultObject


class ObjectTree(TreeItem):
    newInstance = 1
    defaultName = "Object"

    def __init__(self, defaults=True, **kwargs):
        super().__init__(**kwargs)
        self.dragable = False
        self.dropable = True
        self.filename = None
        if defaults:
            self.createDefaultObjects()


    @classmethod
    def newObjectTree(cls, mainWin):
        name = "{:s}{:d}".format(cls.defaultName, cls.newInstance)
        cls.newInstance += 1
        return cls(mainWin=mainWin, name=name)


    @classmethod
    def fromParameters(cls, mainWin, parameters):
        parameters['defaults'] = False
        return cls(mainWin=mainWin, **parameters)
    

    def createDefaultObjects(self):
        """ Creates default child objects that are always shown in the tree.
        
        Subclasses should overide this to control what defaults are created.
        """
        default1 = DefaultObject(mainWin=self.mainWin, name="Default1")
        default1.parent = self
        default2 = DefaultObject(mainWin=self.mainWin, name="Default2")
        default2.parent = self
    

    def save(self, filename):
        """ Saves the ObjectTree to file. """
        if not os.path.exists(os.path.dirname(filename)):
            return False
        data = self.buildSaveDict()
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True


    def buildSaveDict(self):
        data = {}
        self.saveNode(data, self)
        return data


    def saveNode(self, data, parent):
        data['parameters'] = parent.parameters
        data['class'] = type(parent).__name__
        data['children'] = []
        if len(parent.children) > 0:
            for child in parent.children:
                childData = {}
                data['children'].append(childData)
                self.saveNode(childData, child)


    @classmethod
    def load(cls, mainWin, filename):
        """ Constructs an ObjectTree from a given file. """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        objectTree = cls.fromParameters(mainWin, data['parameters'])
        for child in data['children']:
            objectTree.createNode(child, objectTree, mainWin)
        return objectTree


    @classmethod
    def createNode(cls, data, parent, mainWin):
        parameters = data['parameters']
        clsType = data['class']
        item = cls.createClass(clsType, mainWin, parameters)
        item.parent = parent
        for child in data['children']:
            cls.createNode(child, item, mainWin)


    @classmethod
    def createClass(cls, clsType, mainWin, parameters):
        """ Map the class names onto constructors.
        
        Subclasses need to implement this to correctly load data.
        """
        if clsType == "DefaultObject":
            return DefaultObject.fromParameters(mainWin, parameters)
        if clsType == "ItemNode":
            return ItemNode.fromParameters(mainWin, parameters)


    # TODO, get rid of this once we get stuff tested
    def createItem(self):
        item = ItemNode.newItemNode(mainWin=self.mainWin)
        return item


class ItemNode(TreeItem):
    newInstance = 1
    defaultName = "Item"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropable = False


    @classmethod
    def newItemNode(cls, mainWin):
        name = "{:s}{:d}".format(cls.defaultName, cls.newInstance)
        cls.newInstance += 1
        return ItemNode(mainWin=mainWin, name=name)


    def iconPath(self):
        # The icon function is defined here to change the icon
        location = 'icons'
        name = 'new.png'
        return location, name


# TODO, implement this
class FolderNode(TreeItem):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)


    def iconPath(self):
        # The icon function is defined here to change the icon
        location = 'icons'
        name = 'open.png'
        return location, name