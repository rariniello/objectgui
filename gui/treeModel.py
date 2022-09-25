import sys
from objectgui.gui import util

from PyQt5.QtWidgets import (
    QWidget
)

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QMimeData

from objectgui.core.tree import NodeMixin


class RootNode(NodeMixin):
    """ Blank node class for the invisible root node. """
    def __init__(self):
        super().__init__()
        self.name = "Root"


class DragMimeData(QMimeData):
    """ Custom Mime data object so we can pass the tree item indexes directly. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indexes = []
    
    def add_index(self, index):
        """ Adds the given index to the Mime data's indexes list. """
        self.indexes.append(index)

        
class TreeModel(QtCore.QAbstractItemModel):
    # I have no idea how some of this works, just translated the qt example into python
    def __init__(self, objectTree):
        super().__init__()
        # The root node is hidden so we make an empty root and make our root its child
        self.rootItem = RootNode()
        objectTree.parent = self.rootItem
        self.objectTree = objectTree


    def index(self, row, column, parentInd):
        """ Returns the index of the item in the model from the given row, column and parent index. """
        if not self.hasIndex(row, column, parentInd):
            return QtCore.QModelIndex()

        if not parentInd.isValid():
            parent = self.rootItem
        else:
            parent = parentInd.internalPointer()
        child = parent.children[row]
        return self.createIndex(row, column, child)


    def parent(self, index):
        """ Returns the parent of the model item with the given index. """
        if not index.isValid():
            return QtCore.QModelIndex()
        child = index.internalPointer()
        parent = child.parent

        if parent == self.rootItem:
            return QtCore.QModelIndex()
        return self.createIndex(parent.row, 0, parent)


    def rowCount(self, parentInd):
        """ Returns the number of children under the given parent index. """
        if parentInd.column() > 0:
            return 0
        
        if not parentInd.isValid():
            parent = self.rootItem
        else:
            parent = parentInd.internalPointer()
        return len(parent.children)


    def columnCount(self, parentInd):
        """ Returns the number of columns for the children of the given parent index. """
        if parentInd.isValid():
            return parentInd.internalPointer().columnCount()
        else:
            return self.objectTree.columnCount()


    def data(self, index, role):
        """ Returns the data stored under the given role for the item with the given index. 
        
        Args:
          index: Index for the tree item being requested.
          role: The type of data requested by the view, see Qt.ItemDataRole.
        """
        if not index.isValid():
            return None
        item = index.internalPointer()
        # Use index.column for multiple columns
        if role == Qt.DisplayRole:
            return item.displayData(index.column())
        elif role == Qt.DecorationRole:
            args = item.iconPath()
            return QtGui.QIcon(util.iconPath(*args))
        elif role == Qt.EditRole:
            return None
        elif role == Qt.ToolTipRole:
            return None
        else:
            return None


    def flags(self, index):
        """ Returns the item flags for the given index.
        
        Args:
          index: Index for the tree item being requested.
        
        Returns:
          flags: Bitwise-or of flags defined in Qt.ItemFlags.
        """
        if not index.isValid():
            #return Qt.ItemIsDropEnabled
            return Qt.NoItemFlags
        item = index.internalPointer()
        flags = Qt.ItemFlag()
        if not item.suppressed:
            flags |= Qt.ItemIsEnabled
        if item.dragable:
            flags |= Qt.ItemIsDragEnabled
        if item.dropable:
            flags |= Qt.ItemIsDropEnabled
        #flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        return flags

    # Drag drop methods
    # -------------------------------------------------------------------------
    def supportedDropActions(self):
        """ Returns the drop actions supported by this model. """
        return Qt.MoveAction
    

    def mimeData(self, indexes):
        """ Create the Mime data that is provided to the drop event.
        
        A subclass of QMimeData is used to pass the indexes directly to the drop handler.
        """
        mimedata = DragMimeData()
        encoded_data = QtCore.QByteArray()
        stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.WriteOnly)
        for index in indexes:
            if index.isValid():
                item = index.internalPointer()
                mimedata.add_index(index)
                text = item.name
        stream << QtCore.QByteArray(text.encode('utf-8'))
        mimedata.setData('application/x-qabstractitemmodeldatalist', encoded_data)
        return mimedata
    

    def canDropMimeData(self, data, action, row, column, parentInd):
        """ Returns if the item can be dropped or not. """
        allow = super().canDropMimeData(data, action, row, column, parentInd)
        if not parentInd.isValid():
            return allow
        else:
            parent = parentInd.internalPointer()
        
        childInd = self.index(row, column, parentInd)
        if childInd.isValid():
            child = childInd.internalPointer()
            if child.default:
                allow = False

        # print(allow, row)
        return allow


    def dropMimeData(self, data, action, row, column, parentInd):
        """ Handles drop event, only move actions are allowed. """
        if action == Qt.MoveAction:
            # Use this code if you ever want to extract the actual Mime data
            # encoded_data = data.data('application/x-qabstractitemmodeldatalist')
            # stream = QtCore.QDataStream(encoded_data, QtCore.QIODevice.ReadOnly)

            # new_items = []
            # rows = 0
            # while not stream.atEnd():
            #     text = QtCore.QByteArray()
            #     stream >> text
            #     text = bytes(text).decode('utf-8')
            #     new_items.append((text))
            #     rows += 1  

            indexes = data.indexes
            i = 0
            # If dropped on the parent, move to the end of the parent
            if row == -1:
                row = self.rowCount(parentInd)
            for index in indexes:
                item = index.internalPointer()
                sourceParentInd = self.parent(index)
                sourceRow = item.row
                # print("Target:", item.name, sourceRow, row + i)
                self.moveRows(sourceParentInd, sourceRow, 1, parentInd, row + i)
                i += 1
                # Handle cases where some rows are before the drop point
                if self.parent(index) == parentInd and sourceRow < row:
                    row -= 1

            return True
        else:
            return False


    def moveRows(self, sourceParentInd, sourceRow, count, destinationParentInd, destinationRow):
        """ Moves a item from one parent/row combination to a different parent/row combination. """
        # Return flase if we try and move an object ontop of itself
        # This handles issues that occur when multiple rows are selected
        if sourceParentInd == destinationParentInd and sourceRow == destinationRow:
            return False
        if sourceParentInd == destinationParentInd and sourceRow == destinationRow - 1:
            return False
        
        # XXX An invalid index is thrown when a item outside a folder is selected, followed by an item
        # inside the folder and the resulting combo is dragged onto the folder 
        # the items appear to be moved correctly by 

        # Tell the view the info it needs to move the items persistent indexes
        sourceLast = sourceRow + count - 1
        # print(sourceRow, destinationRow)
        self.beginMoveRows(sourceParentInd, sourceRow, sourceLast, destinationParentInd, destinationRow)

        if not sourceParentInd.isValid():
            sourceParent = self.rootItem
        else:
            sourceParent = sourceParentInd.internalPointer()

        # Source and destination parents are the same
        if sourceParentInd == destinationParentInd:
            for i in range(count):
                item = sourceParent.children[sourceRow]
                if sourceRow < destinationRow:
                    item.row = destinationRow - 1
                else:
                    item.row = destinationRow + i
        # Source and destination parents are different
        else:
            if not destinationParentInd.isValid():
                destinationParent = self.rootItem
            else:
                destinationParent = destinationParentInd.internalPointer()
            for i in range(count):
                item = sourceParent.children[sourceRow]
                item.parent = destinationParent
                item.row = destinationRow + i

        # print("Moved to:", item.name, item.row)
        # Tell the view we are done moving so it can go ahead and update/verify indexes
        self.endMoveRows()
        return True


    # Changing elements in the tree
    # -------------------------------------------------------------------------
    def insertRows(self, row, count, parentInd, indexes):
        return False


    def addRow(self, row, parentInd, item):
        """ Adds the passed item to the tree at the given parent and row. """
        if row == -1:
            row = self.rowCount(parentInd)
        self.beginInsertRows(parentInd, row, row)

        if not parentInd.isValid():
            parent = self.rootItem
        else:
            parent = parentInd.internalPointer()
        item.parent = parent
        item.row = row
        self.endInsertRows()
        return True


    def removeRows(self, row, count, parentInd):
        """ Removes count rows from the model starting with the given row under the given parent. """
        # XXX Remove rows gets called after items are moved with a drag-drop event
        # It tries to remove the rows we just moved, if this method is implemented, it breaks things
        
        # if not parentInd.isValid():
        #     parent = self.rootItem
        # else:
        #     parent = parentInd.internalPointer()

        # self.beginRemoveRows(parentInd, row, row + count - 1)
        # for i in range(count):
        #     child = parent.children[row]
        #     child.parent = None
        # self.endRemoveRows()
        # return True
        return False
