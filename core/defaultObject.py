from objectgui.core.treeItem import TreeItem


class DefaultObject(TreeItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dragable = False
        self.dropable = False
        self.default = True
    

    def iconPath(self):
        # The icon function is defined here to change the icon
        location = 'icons'
        name = 'settings.png'
        return location, name