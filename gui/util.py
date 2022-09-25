import os
import objectgui.config as config


def iconPath(*args):
    """ Loads an icon in the given resource subdirectory. 
    
    Use 3 arguments to specifiy a base directory. 
    
    Args:
        location: The subdirectory in resources where the icon is located.
        name: Filename of the icon.
        base: Optional, path to the resources folder.
    """
    if len(args) >= 2:
        location = args[0]
        name = args[1]
        if len(args) == 2:
            return os.path.join(config.objectguiPath, 'resources', location, name)
        else:
            base = args[2]
            return os.path.join(base, 'resources', location, name)

        