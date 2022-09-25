import os
import sys


objectguiPath = None


def defPaths():
    global objectguiPath

    objectguiPath = getObjectguiPath()


def getObjectguiPath():
    base = __file__
    path = os.path.dirname(os.path.realpath(os.path.abspath(base)))
    return path