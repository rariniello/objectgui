import sys
import os
from PyQt5 import uic
from PyQt5 import pyrcc_main


# TODO when we split this off into its own package, remove objectgui from paths
def map(uiDirName, uiModName):
    return os.path.join('objectgui', 'gui', 'ui'), "ui_"+uiModName


def build_ui():
    uic.compileUiDir(os.path.join('objectgui', 'designer'), map=map)
    resourceFile = os.path.join('objectgui', 'resources', 'resources.qrc')
    fileOut = os.path.join('objectgui', 'resources_rc.py')
    pyrcc_main.processResourceFile([resourceFile], fileOut, False)


if __name__ == '__main__':


    build_ui()
    sys.exit()