from typing import Tuple, Callable

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QMenu
)

from objectgui.core.tree import NodeMixin
from objectgui.gui.editObject import EditObject


# QObject is needed in order to emit signals
class Node(NodeMixin, QObject):
    """ Class that controls how a node behaves when viewed in the gui.
    
    Adds an interface to a tree node to interact with the gui.
    Implement methods in the subclass to change how the gui behaves.
    """
    editSubmitted = pyqtSignal()
    editCancelled = pyqtSignal()

    # Attributes that control save/load behavior
    ownFile = False
    # Attributes that control drag/drop behavior
    dragable = True
    dropable = True
    # Other attributes
    suppressed = False
    default = False
    columnCount = 1 # The number of data columns to display for the children of this node
    editFormInnerClass = None # subclasses need to set this attribute to create the form
    # Come up with default names for the classes
    newInstance = 1
    defaultName = "File"

    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

        # Initialization work
        self.__attributes = {}
        self.addAttribute('name')
        #self.addActionsToMenu('name')
        self._createEditForm()


    @classmethod
    def newNode(cls, **kwargs):
        """ Creates a new node with a unique identifier. """
        name = "{:s}{:d}".format(cls.defaultName, cls.newInstance)
        cls.newInstance += 1
        node = cls(name=name, **kwargs)
        node.createDefaultObjects()
        return node


    @classmethod
    def fromAttributes(cls: str, attributes: dict) -> object:
        """ Creates an instance of the class from the given parameters dictionary.

        Subclasses can override this method if they need to modify the instance creation process.
        
        Return:
            Node: Instance of the Node class created from the parameters dictionary.
        """
        return cls(**attributes)

    
    def addAttribute(self, name: str, getter: Callable=None, setter: Callable=None):
        """ Adds an attribute of the main class to the node
        
        The full set of attributes for the class should be sufficient to recreate the class.
        Attributes will be saved to disk when the ObjectTree is saved and loaded from disk
        when the tree is loaded. They are also used to reset the object to its prior state
        when clicking cancel on an edit gui.

        Args:
            name: The name of the attribute, will be displayed in the save file.
            getter: The function to get the attribute from the main class. If not defined,
                will set the class a
            setter: The function to set the attribute in the main class.
        """
        if not isinstance(name, str):
            raise TypeError("Attribute name must be a string.")
        if getter is None:
            getter = lambda: getattr(self, name)
        if setter is None:
            setter = lambda x: setattr(self, name, x)
        if not callable(getter) or not callable(setter):
            raise TypeError("Getter and setter must be callable.")
        self.__attributes[name] = {
            'getter': getter,
            'setter': setter
        }
    

    def updateAttributes(self, attributes: dict):
        """ Updates the object to the state specified by the given attributes. 
        
        Args:
            attributes: Dictionary of attribute name/value pairs.
        """
        for name, value in attributes.items():
            self.__attributes[name]['setter'](value)


    def getAttributes(self):
        """ Compiles the classes attributes and their current values into a dictionary.
        
        Returns:
            attributes: Dictionary {name: value} of all the attributes in the class.
        """
        # TODO Do we need to worry about copying here if the attribute is an array?
        # Would the attribute ever be an array? they are meant to be set using fields in a gui
        # If it should never be an array then it should throw an error or something
        attributes = {}
        for name, attr in self.__attributes.items():
            attributes[name] = attr['getter']()
        return attributes


    def cacheAttributes(self):
        """ Saves the class attributes when the edit window is shown. 
        
        If the window is then closed by cancelling, the chached attributes are used to reset the object.
        """
        self.__cache = self.getAttributes()
    

    def restoreAttributesFromCache(self):
        """ Saves the class attributes when the edit window is shown. 
        
        If the window is then closed by cancelling, the chached attributes are used to reset the object.
        """
        self.updateAttributes(self.__cache)
    

    def createSaveData(self):
        """ Builds the dictionary that will be saved to disk for this class.
        
        Subclasses can use this to customize what data they save. The return value must be able
        to be serialized with json.

        Returns:
            attributes: Dictionary {name: value} of all the attributes in the class.
        """
        return self.getAttributes()

    
    def createDefaultNodes(self):
        """ Creates default child nodes that are always shown in the tree.
        
        Subclasses should overide this to control what defaults are created.
        """
        pass
    

    # GUI interaction methods
    # -------------------------------------------------------------------------
    def getDisplayData(self, column: int) -> str:
        """ Returns the display text for the given column of this item.

        Args:
            column: The tree column to return the display text for.
        
        Returns:
            displayText: Text that will be displayed by the tree view.
        """
        if column == 0:
            return self.name
        else:
            return ""
    

    # XXX consider just making these attributes of the class rather than a function subclasses need to override
    # But maybe we don't want to so we have an easy default? Could have default attribute values as well, maybe path issues?
    def iconPath(self) -> Tuple[str, str]:
        """ Returns the path to the icon to display on the tree view for this item.

        Subclasses should override this method to add actions to the context menu.        
        See gui.util.iconPath for more on how the path is constructed.

        Returns:
            location: Directory name within resources/ where the icon is located.
            name: Filename of the icon image.
        """
        location = 'icons'
        name = 'test.png'
        return location, name
    

    # XXX Not sure if I like this structure of passing actions down through the application
    def addActionsToMenu(self, menu: QMenu, actions) -> QMenu:
        """ Creates the context menu when the user right clicks on the tree item.

        Subclasses should override this method to add actions to the context menu.
        
        Args:
            menu: An empty menu that subclasses can add actions to.
            actions: Dictionary of all actions in the program.

        Returns:
            menu: The menu after adding actions.
        """
        return menu
    

    def _createEditForm(self):
        """ Creates the edit form for the object.
        
        The edit form is the outer edit box that contains the cancel and submit button.
        """
        self.editForm = EditObject()
        self.editForm.cancelButton.clicked.connect(self.cancelForm)
        self.editForm.okButton.clicked.connect(self.submitForm)
        self.editForm.parent = self
        if self.editFormInnerClass is not None:
            self.editFormInner = self.editFormInnerClass(self)
            self.editForm.editFormInner = self.editFormInner
            self.editForm.scrollArea.setWidget(self.editFormInner)
        else:
            # Do nothing, nodes are allowed not to have edit forms; for example, the fileNode doesn't
            pass
    

    def submitForm(self):
        """ Emits the edit submitted signal.
        
        Subclasses can override this if they want to do more complex logic when submit is clicked.
        """
        self.editSubmitted.emit()
    

    def cancelForm(self):
        """ Resets the object attributes and emits the edit cancelled signal.
        
        Subclasses can override this if they want to do more complex logic when cancel is clicked.
        """
        self.restoreAttributesFromCache()
        self.editCancelled.emit()
    

    # XXX Not sure I want to add this capability
    def assignFieldToAttribute(self, field: object, attribute: str, fieldConv=None, attrConvert=None):
        """ Assigns a field on the edit form to an atribute of the class. 
        
        Args:
            field: 
            attribute: 
        """
        if hasattr(field, 'editingFinished'):
            setter = self.__attributes[attribute]['setter']
            field.editingFinished.connect(setter)
        self.__attributes[attribute]['field'] = field
    

    def updateFieldsFromAttributes(self):
        for name, attr in self.__attributes.items():
            if 'field' in attr:
                field = attr['field']
                if 'setValue' in field:
                    field.setValue(attr['getter']())
