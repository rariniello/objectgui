from objectgui.core.node import Node


class DefaultNode(Node):
    def __init__(self, **kwargs):
        self.dragable = False
        self.dropable = False
        self.default = True
        super().__init__(**kwargs)
    

    def iconPath(self):
        # The icon function is defined here to change the icon
        location = 'icons'
        name = 'settings.png'
        return location, name