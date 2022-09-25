class NodeMixin():
    """ Mixin class that allows objects to be part of a tree. 
    
    Nothing in this code stops a loop being created, use carefully.
    """
    def __init__(self, *args, **kwargs):
        self.__parent = None
        self.__children = []
        super().__init__(*args, **kwargs)


    @property
    def parent(self):
        """ Returns this objects parent in the tree, None if this object is the root. """
        return self.__parent


    @parent.setter
    def parent(self, value):
        """ Change this items parent, the standard way to move things around the tree. """
        parent = self.__parent
        if parent is not value:
            self.__detach(parent)
            self.__attach(value)


    def __detach(self, parent):
        """ Remove this object from the old parent's children by rebuilding the children array. """
        if parent is not None:
            parentsChildren = parent.__children
            parentsChildren.remove(self)
            self.__parent = None


    def __attach(self, parent):
        """ Append this object to the end of the new parents children array. """
        if parent is not None:
            parentsChildren = parent.__children
            parentsChildren.append(self)
            self.__parent = parent


    @property
    def children(self):
        """ Returns the list of children of this object. """
        return self.__children


    @children.setter
    def children(self, children):
        """ Change the children of an this object, accomplished by changing each child's parent. 
        
        Args:
          children: List of children to set.
        """
        del self.children
        for child in children:
            child.parent = self


    @children.deleter
    def children(self):
        """ Remove all children of this object and set all children's parents to None. """
        for child in self.children:
            child.parent = None


    @property
    def root(self):
        """ Returns the root node of the tree. """
        node = self
        while node.parent is not None:
            node = node.parent
        return node
    

    @property
    def row(self) -> int:
        """ Returns the index of this object in its parent's children list. """
        parent = self.__parent
        parentsChildren = parent.__children
        return parentsChildren.index(self)
    
    @row.setter
    def row(self, value: int):
        """ Moves this object to a given index within its parent's children list. """
        if self.__parent is not None:
            parent = self.__parent
            parentsChildren = parent.__children
            parentsChildren.remove(self)
            parentsChildren.insert(value, self)


    def isRoot(self):
        return self.parent is None
