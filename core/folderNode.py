from objectgui.core.node import Node

# TODO, implement this
class FolderNode(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    

    def iconPath(self):
        # The icon function is defined here to change the icon
        location = 'icons'
        name = 'folder.png'
        return location, name