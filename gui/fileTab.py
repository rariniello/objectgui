import os
import sys
from objectgui.gui import util

from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QMenu, QHeaderView
)

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import pyqtSlot

from objectgui.gui.ui.ui_FileTab import Ui_FileTabWidget
from objectgui.gui.treeModel import TreeModel


class FileTab(QWidget, Ui_FileTabWidget):
    saveFilter = "Project File (*.json)"
    openFilter = "Project File (*.json)"

    def __init__(self, name, mainWin, objectTree, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.name = name
        self.mainWin = mainWin
        self.objectTree = objectTree
        self.lastPath = ""

        self.model = self.createTreeModel(objectTree)
        self.objectTreeView.setModel(self.model)
        index = self.model.index(0, 0, QtCore.QModelIndex())
        self.objectTreeView.setExpanded(index, True)
        self.setupTreeHeader()

        self.objectTreeView.customContextMenuRequested.connect(self.openMenu)

    
    def createTreeModel(self, objectTree):
        """ Creates a new treeModel. 
        
        Implement this method in the FileTab subclass if you subclass the TreeModel.
        """
        return TreeModel(objectTree)
    

    def setupTreeHeader(self):
        """ Make it so a horizontal scroll bar appears on the tree rather than ellipses. """
        header = self.objectTreeView.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)

    
    def createContextMenu(self, clickedItem, point):
        """ Creates the context menu when right clicking on tree items. """
        menu = QMenu()
        menu = clickedItem.createContextMenu(menu)
        menu.exec_(self.objectTreeView.viewport().mapToGlobal(point))

    
    def showEditObjectWidget(self, widget):
        layout = self.featureLayout
        widget.parent.cacheData()
        self.objectTreeView.hide()
        layout.replaceWidget(self.objectTreeView, widget)
        widget.show()
    

    def hideEditObjectWidget(self):
        layout = self.featureLayout
        widget = layout.itemAt(0).widget()
        widget.hide()
        layout.replaceWidget(widget, self.objectTreeView)
        self.objectTreeView.show()
    

    def save(self):
        """ Save the currently active tab to the existing filename. """
        # If the current tab has never been saved then call save as
        objectTree = self.objectTree
        if objectTree.filename is None:
            self.save_as()
        else:
            objectTree.save(objectTree.filename)
    

    def save_as(self):
        """ Save the currently active tab as a new filename. """
        objectTree = self.objectTree
        # If we call save as on a tab with an exisitng filename, open the dir of the file
        if objectTree.filename is not None:
            dirname = os.path.dirname(objectTree.filename)
        else:
            dirname = self.lastPath
        
        # Open a system specific file browser
        objectTree.filename = QFileDialog.getSaveFileName(self, "Save As", dirname, self.saveFilter)[0]
        name = os.path.splitext(os.path.split(objectTree.filename)[1])[0]
        oldName = objectTree.name
        objectTree.name = name

        if objectTree.save(objectTree.filename):
            self.mainWin.addRecentlyOpened(objectTree.filename)
        else:
            objectTree.name = oldName
    
    @pyqtSlot(QPoint)
    def openMenu(self, point):
        index = self.objectTreeView.indexAt(point)
        clickedItem = index.internalPointer()

        # Can use selected items because they update before the context menu is called
        # Let the actions handle finding the selected items
        # indexes = self.objectTreeView.selectedIndexes()
        # for index in indexes:
        #     item = index.internalPointer()
        
        self.createContextMenu(clickedItem, point)
