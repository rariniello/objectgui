import os
import sys
import json
from objectgui.gui import util

from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QAction
)
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot

from objectgui.gui.fileTab import FileTab
# We must do thi before importing ui_MainWindow
#import objectgui.resources_rc
#sys.modules['resources_rc'] = objectgui.resources_rc

import objectgui.gui.ui.ui_MainWindow as ui_MainWindow

from objectgui.core.objectTree import ObjectTree


class MainWindow(QMainWindow, ui_MainWindow.Ui_MainWindow):
    recentlyOpenedSave = 'data/recentlyOpened.json'
    lastPathSave = 'data/lastPath.json'


    def __init__(self, parent=None, icon=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalSlots()

        if icon is None:
            icon = QtGui.QIcon(util.iconPath('icons', 'icon32x32'))
        self.setWindowIcon(icon)

        self.lastPath = ""
        self.recentlyOpened = []
        self.loadRecentlyOpened()
        self.loadLastPath()
        

    def connectSignalSlots(self):
        # Slots for all the window actions
        self.actionNew.triggered.connect(self.new)
        self.actionOpen.triggered.connect(self.open)
        self.actionSave.triggered.connect(self.save)
        self.actionSave_As.triggered.connect(self.save_as)
        self.actionSave_All.triggered.connect(self.save_all)
        self.actionPrint.triggered.connect(self.print)
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionSuppress.triggered.connect(self.suppress)
        self.actionUnsuppress.triggered.connect(self.unsuppress)
        self.actionSettings.triggered.connect(self.settings)

        # Slots for things other than actions
        self.fileTabs.tabCloseRequested.connect(self.closeTabDialog)
    

    @property
    def activeTab(self):
        """ Returns the currently active fileTab. """
        return self.fileTabs.currentWidget()

    
    @property
    def activeTabInd(self):
        """ Returns the currently active fileTab. """
        return self.fileTabs.currentIndex()


    def enableTabActions(self):
        """ Enable the actions that cannot ocur until a tab is created. """
        self.actionSave.setEnabled(True)
        self.actionSave_As.setEnabled(True)
        self.actionSave_All.setEnabled(True)
        self.actionPrint.setEnabled(True)
        self.actionSuppress.setEnabled(True)
        self.actionUnsuppress.setEnabled(True)
    

    def disableTabActions(self):
        """ Disable the tab actions that can only occur once a tab is created. """
        self.actionSave.setEnabled(False)
        self.actionSave_As.setEnabled(False)
        self.actionSave_All.setEnabled(False)
        self.actionPrint.setEnabled(False)
        self.actionSuppress.setEnabled(False)
        self.actionUnsuppress.setEnabled(False)


    def updateTabNames(self):
        """ Updates the names of the tabs based on the objectTree names. """
        fileTabs = self.fileTabs
        for i in range(fileTabs.count()):
            tab = fileTabs.widget(i)
            fileTabs.setTabText(i, tab.objectTree.name)
    

    def createNewTab(self, objectTree):
        """ Creates a new tab, sets the icon, and makes it the active tab. """
        fileTabs = self.fileTabs
        tab = self.createFileTab(objectTree)
        # Provide a default location for the save_as dialog for a new file
        tab.lastPath = self.lastPath
        args = objectTree.iconPath()
        fileTabs.addTab(tab, QtGui.QIcon(util.iconPath(*args)), objectTree.name)
        fileTabs.setCurrentWidget(tab)

        # If this is the first tab added, enable save buttons etc.
        if fileTabs.count() == 1:
            self.enableTabActions()


    def closeTab(self, index):
        fileTabs = self.fileTabs
        tab = fileTabs.widget(index)
        fileTabs.removeTab(index)
        if fileTabs.count() == 0:
            self.disableTabActions()
    

    def hideEditForm(self):
        self.activeTab.hideEditObjectWidget()


    def createFileTab(self, objectTree):
        """ Creates the file tab object. 
        
        Implement this method in the MainWindow subclass if you subclass the FileTab.
        """
        return FileTab(objectTree.name, self, objectTree)


    def createNewObjectTree(self):
        """ Creates a new objectTree. 
        
        Implement this method in the MainWindow subclass if you subclass the ObjectTree.
        """
        return ObjectTree.newObjectTree(self)


    def loadObjectTree(self, filename):
        """ Creates a new objectTree. 
        
        Implement this method in the MainWindow subclass if you subclass the ObjectTree.
        """
        return ObjectTree.load(self, filename)


    def addRecentlyOpened(self, filename):
        """ Adds a new file to the recently opened files menu. """
        # TODO Check if the file still exists before we add it
        action = QAction(self)
        name = os.path.splitext(os.path.split(filename)[1])[0]
        action.setText(name)
        action.filename = filename
        action.triggered.connect(lambda checked: self.openRecent(checked, action))

        recentlyOpened = self.recentlyOpened
        N = len(recentlyOpened)
        # If the menu is empty, add the first element, otherwise insert at the beginning
        if N > 0:
            self.menuOpen_Recent.insertAction(recentlyOpened[0], action)
        else:
            self.menuOpen_Recent.addAction(action)

        # Insert into a seperate array for tracking purposes
        recentlyOpened.insert(0, action)

        # If the list is too long, get rid of the stuff at the end
        # If it was already in the menu, remove it (effectively move it to the top)
        M = 10
        itemsToRemove = []
        for i in range(1, N+1):
            if (recentlyOpened[i].filename == filename) or (i >= M):
                itemsToRemove.append(recentlyOpened[i])
        for i in range(len(itemsToRemove)):
            recentlyOpened.remove(itemsToRemove[i])
            self.menuOpen_Recent.removeAction(itemsToRemove[i])
            itemsToRemove[i].deleteLater()


    def saveRecentlyOpened(self):
        """ Saves the list of recently opened files to disk. """
        recentlyOpenedFilenames = []
        recentlyOpened = self.recentlyOpened
        N = len(recentlyOpened)
        for i in range(N):
            filename = recentlyOpened[i].filename
            recentlyOpenedFilenames.append(filename)
        
        saveName = os.path.abspath(self.recentlyOpenedSave)
        if not os.path.exists(os.path.dirname(saveName)):
            return False
            # Requires administrator privileges on windows
            # os.makedirs(os.path.dirname(saveName))

        with open(saveName, 'w') as f:
            json.dump(recentlyOpenedFilenames, f)

    
    def loadRecentlyOpened(self):
        """ Loads the list of recently opened files from disk. """
        saveName = os.path.abspath(self.recentlyOpenedSave)
        if not os.path.exists(saveName):
            return False

        with open(saveName, 'r') as f:
            recentlyOpenedFilenames = json.load(f)
        
        # Loop through the list backwards because files are added at the top
        for filename in reversed(recentlyOpenedFilenames):
            self.addRecentlyOpened(filename)
        
        return True


    def saveLastPath(self):
        """ Save the location of the last file opened. """
        saveName = os.path.abspath(self.lastPathSave)
        if not os.path.exists(os.path.dirname(saveName)):
            return False
            # Requires administrator privileges on windows
            # os.makedirs(os.path.dirname(saveName))

        with open(saveName, 'w') as f:
            json.dump(self.lastPath, f)
    

    def loadLastPath(self):
        """ Load the location of the last file opened. """
        saveName = os.path.abspath(self.lastPathSave)
        if not os.path.exists(saveName):
            return False

        with open(saveName, 'r') as f:
            self.lastPath = json.load(f)

    
    def openFile(self, filename):
        # Check if the file is already open, if so activate the tab
        fileTabs = self.fileTabs
        for i in range(fileTabs.count()):
            tab = fileTabs.widget(i)
            if filename == tab.objectTree.filename:
                fileTabs.setCurrentWidget(tab)
                return
        
        # If the file path exists, load the file
        if os.path.exists(os.path.dirname(filename)):
            self.addRecentlyOpened(filename)
            self.lastPath = os.path.dirname(filename)
            objectTree = self.loadObjectTree(filename)
            objectTree.filename = filename
            self.createNewTab(objectTree)


    @pyqtSlot()
    def new(self):
        """ Create a new file: create a new object tree and add a fileTab. """
        objectTree = self.createNewObjectTree()
        self.createNewTab(objectTree)


    @pyqtSlot()
    def open(self):
        """ Open an existing file: create objects from a saved file and add a fileTab. """
        filename = QFileDialog.getOpenFileName(self, "Open", self.lastPath, FileTab.openFilter)[0]
        self.openFile(filename)
    

    @pyqtSlot(bool, object)
    def openRecent(self, checked, action):
        self.openFile(action.filename)


    @pyqtSlot()
    def save(self):
        """ Save the currently active tab to the existing filename. """
        self.activeTab.save()
        self.updateTabNames()


    @pyqtSlot()
    def save_as(self):
        """ Save the currently active tab as a new filename. """        
        self.activeTab.save_as()
        self.updateTabNames()


    @pyqtSlot()
    def save_all(self):
        """ Save all open tabs to the existing filenames. """
        fileTabs = self.fileTabs
        for i in range(fileTabs.count()):
            tab = fileTabs.widget(i)
            tab.save()
        self.updateTabNames()


    @pyqtSlot()
    def print(self):
        """ Save a visual representation of the data part of the currently active tab. """
        pass


    @pyqtSlot()
    def undo(self):
        """ Undo the last undoable user action. """
        # I think I will handle this by decorating each undoable action
        # Then I track actions and arguments so I can do the inverse
        pass


    @pyqtSlot()
    def redo(self):
        """ Redo the last undoable user action. """
        pass


    @pyqtSlot()
    def suppress(self):
        """ Suppress all selected items in the tree. """
        pass


    @pyqtSlot()
    def unsuppress(self):
        """ Unsuppress all selected items in the tree. """
        pass


    @pyqtSlot()
    def settings(self):
        """ Unsuppress all selected items in the tree. """
        pass


    @pyqtSlot(int)
    def closeTabDialog(self, index):
        """ Open a closed tab dialog if the window has not been saved. """
        # This will probably be easier to do once the undo functionality is implemented
        self.closeTab(index)


    def closeEvent(self, event):
        """ Reimplements the close event to handle clean-up operations. """
        self.saveRecentlyOpened()
        self.saveLastPath()
        # TODO, check if files are saved and prompt if not
        # Better handled attaching to the close signal of the tab
        
        event.accept()