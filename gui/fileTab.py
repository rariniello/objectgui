import os
import sys
from objectgui.gui import util

from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QMenu, QHeaderView, QToolBar, QAction, QMainWindow
)

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtCore import pyqtSlot

from objectgui.gui.ui.ui_FileTab import Ui_FileTabWidget
from objectgui.gui.treeModel import TreeModel
from objectgui.core.fileNode import FileNode


class FileTab(QMainWindow, Ui_FileTabWidget):
    """ A class representing a file tab in the GUI. 

    Each fileTab contains a top level fielNode object and includes functionality
    for creating and saving files.

    Attributes:
        saveFilter (str): The filter to use when saving files. Defaults to "Project File (*.json)".
        openFilter (str): The filter to use when opening files. Defaults to "Project File (*.json)".
        fileNodeCls (class): The class to use for file nodes. Defaults to FileNode. 

    Signals:
        saveSuccessful(str): Emitted when a file is saved successfully. Contains the filename.

    Methods:
        newFileTab(): Returns a new, empty FileTab instance.
        load(filename: str): Returns a new FileTab instance with the contents of the specified file.
        save(): Saves the current file.
        save_as(): Saves the current file with a new filename.
        addNode(node): Adds gui functionality to the given node by connecting signals and slots.
        showEditObjectWidget(widget): Shows the given editForm in the location where the object tree normally is.
        openMenu(point): Displays an appropriate context menu at the given point on the tree view.
    """
    saveFilter = "Project File (*.json)"
    openFilter = "Project File (*.json)"
    fileNodeCls = FileNode

    saveSuccessful = pyqtSignal(str)

    def __init__(self, name, fileNode, actions, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.name = name
        self.fileNode = fileNode
        self.lastPath = ""
        self.actions = actions
        self.editWidgetVisible = False

        self.model = TreeModel(fileNode)
        self.objectTreeView.setModel(self.model)
        index = self.model.index(0, 0, QtCore.QModelIndex())
        self.objectTreeView.setExpanded(index, True)
        self._setupTreeHeader()

        self.objectTreeView.customContextMenuRequested.connect(self.openMenu)

    
    @classmethod
    def newFileTab(cls, actions):
        """ Returns a new, empty FileTab instance. """
        fileNode = cls.fileNodeCls.newNode()
        fileTab = cls(fileNode.name, fileNode, actions)
        fileTab.connectNodes()
        return fileTab


    @classmethod
    def load(cls, filename, actions):
        """ Returns a new FileTab instance constructed from the contents of the specified file. """
        fileNode = cls.fileNodeCls.load(filename)
        fileTab = cls(fileNode.name, fileNode, actions)
        fileTab.connectNodes()
        return fileTab
    

    def addNode(self, node):
        """ Adds gui functionality to the given node by connecting signals and slots. 
        
        Args:
            node: Tree node to add to the gui.
        """
        model = self.model
        parentInd = model.createIndex(0, 0, self.fileNode)
        rowCount = model.rowCount(parentInd)
        self.model.addRow(rowCount, parentInd, node)

        self.connectNodeSignals(node)
    

    def connectNodeSignals(self, node):
        node.editSubmitted.connect(self.hideEditObjectWidget)
        node.editCancelled.connect(self.hideEditObjectWidget)
    

    def connectNodes(self):
        for i, node in enumerate(self.fileNode.iterSubTree()):
            self.connectNodeSignals(node)
    

    def _setupTreeHeader(self):
        """ Makes it so a horizontal scroll bar appears on the tree rather than ellipses. """
        header = self.objectTreeView.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)

    
    def _createContextMenu(self, clickedItem, point):
        """ Creates the context menu when right clicking on tree items. """
        # TODO add default things like suppress to this menu
        menu = QMenu()
        menu = clickedItem.addActionsToMenu(menu, self.actions)
        menu.exec_(self.objectTreeView.viewport().mapToGlobal(point))

    
    def showEditObjectWidget(self, widget):
        """ Shows the given editForm in the location where the object tree normally is.

        Args:
            widget: The editForm to display in the FileTab.
        """
        if self.editWidgetVisible:
            return
        layout = self.featureLayout
        widget.parent.cacheAttributes()
        self.objectTreeView.hide()
        layout.replaceWidget(self.objectTreeView, widget)
        widget.show()
        self.editWidgetVisible = True
        self.enableDisableActions(False)
    

    def hideEditObjectWidget(self):
        """ Hides any visible editForm and shows the object tree. """
        layout = self.featureLayout
        widget = layout.itemAt(0).widget()
        widget.hide()
        layout.replaceWidget(widget, self.objectTreeView)
        self.objectTreeView.show()
        self.editWidgetVisible = False
        self.enableDisableActions(True)
    

    def enableDisableActions(self, state):
        """ Enable or disable all the toolbar actions. """
        for key, action in self.actions.items():
            if state:
                enable = True
                for key, value in action.enableFlags.items():
                    enable = enable and value
                action.setEnabled(enable)
                continue
            action.setEnabled(False)
    

    def save(self):
        """ Saves the currently active tab to the existing filename. """
        # If the current tab has never been saved then call save as
        fileNode = self.fileNode
        if fileNode.filename is None:
            self.save_as()
        else:
            fileNode.save(fileNode.filename)
    

    def save_as(self):
        """ Saves the currently active tab as a new filename. """
        fileNode = self.fileNode
        # If we call save as on a tab with an exisitng filename, open the dir of the file
        if fileNode.filename is not None:
            dirname = os.path.dirname(fileNode.filename)
        else:
            dirname = self.lastPath
        
        # Open a system specific file browser
        filename = QFileDialog.getSaveFileName(self, "Save As", dirname, self.saveFilter)[0]
        # If the user clicks cancel an empty string is returned, in this case do nothing
        if filename == '':
            return
        fileNode.filename = filename
        name = os.path.splitext(os.path.split(fileNode.filename)[1])[0]
        oldName = fileNode.name
        oldfilename = fileNode.filename
        fileNode.name = name

        # Let the application know we have saved the tab with a specific name
        if fileNode.save(fileNode.filename):
            self.saveSuccessful.emit(fileNode.filename)
        else:
            fileNode.name = oldName
            fileNode.filename = oldfilename
    

    @pyqtSlot(QPoint)
    def openMenu(self, point):
        index = self.objectTreeView.indexAt(point)
        clickedItem = index.internalPointer()

        # Can use selected items because they update before the context menu is called
        # Let the actions handle finding the selected items
        # indexes = self.objectTreeView.selectedIndexes()
        # for index in indexes:
        #     item = index.internalPointer()
        
        self._createContextMenu(clickedItem, point)
