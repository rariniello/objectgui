from typing import Tuple

from PyQt5.QtCore import pyqtSlot

from objectgui.core.tree import NodeMixin
from objectgui.gui.editObject import EditObject


class TreeItem(NodeMixin):
    """ Mixin class that controls how an object behaves when viewed in the gui. 
    
    Implement methods in the subclass to change how the gui behaves.
    """
    def __init__(self, mainWin, name, **kwargs):
        self.parameters = {}
        self.parameters['name'] = name
        self.mainWin = mainWin
        super().__init__(**kwargs)
        self.suppressed = False
        self.dragable = True
        self.dropable = True
        self.default = False
        self.createEditForm()


    # Property decorators let us replace superclass attributes with a params object
    @property
    def name(self):
        return self.parameters['name']
    

    @name.setter
    def name(self, value):
        self.parameters['name'] = value
    

    @classmethod
    def fromParameters(cls, mainWin, parameters):
        return cls(mainWin=mainWin, **parameters)
        

    def columnCount(self) -> int:
        """ Returns the number of data columns to display for the children of this item.
        
        Returns:
            columnCount: The number of columns to display for this tree item.
        """
        return 1
    

    def displayData(self, column: int) -> str:
        """ Returns the display text for the given column of this item. 

        Args:
            column: The tree column to return the display text for.
        
        Returns:
            displayText: Text that will be displayed by the tree view.
        """
        return self.name
    

    def iconPath(self) -> Tuple[str, str]:
        """ Returns the path to the icon to display on the tree view for this item.
        
        See gui.util.iconPath for more on how the path is constructed. 

        Returns:
            location: Directory name within resources/ where the icon is located.
            name: Filename of the icon image.
        """
        location = 'icons'
        name = 'test.png'
        return location, name
    

    def createContextMenu(self, menu):
        return menu
    

    def createEditForm(self):
        self.editForm = EditObject()
        self.editForm.cancelButton.clicked.connect(self.cancelForm)
        self.editForm.okButton.clicked.connect(self.submitForm)
        self.editForm.parent = self
    

    def submitForm(self):
        self.mainWin.hideEditForm()
    

    def cancelForm(self):
        self.parameters = self.cache
        self.mainWin.hideEditForm()
    

    def cacheData(self):
        """ Saves the data when the window is shown to allow reverting on cancel. """
        self.cache = self.parameters.copy()
