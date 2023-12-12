import os
import sys

scriptPath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(os.path.join(scriptPath, '..', '..')))

from objectgui.core.node import Node
from objectgui.core.fileNode import FileNode
from objectgui.gui.fileTab import FileTab
import pytest

# Test creating a new file, save action, then cancel dialog

# Test creating a new file, save action, complete dialog, save again

# Test creating a new file, save action, complete dialog, file save fails