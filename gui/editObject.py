import sys

from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QMenu, QHeaderView
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot

# We must do thi before importing ui_EditObject
#import objectgui.resources_rc
#sys.modules['resources_rc'] = objectgui.resources_rc

from objectgui.gui.ui.ui_EditObject import Ui_EditObject


class EditObject(QWidget, Ui_EditObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
