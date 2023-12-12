class NodeMixin():
    """ Mixin class that allows objects to be nodes of a tree. 
    
    Adds an interface to an object to interact with the tree.
    Will throw an error if code attempts to create a loop in the tree
    """
    def __init__(self, *args, **kwargs):
        self.__parent = None
        self.__children = []
        super().__init__(*args, **kwargs)


    @property
    def parent(self) -> object:
        """ Returns this node's parent in the tree, None if this node is the root. """
        return self.__parent


    @parent.setter
    def parent(self, value: object):
        """ Changes this nodes's parent to the given node.
        
        This is the standard way to add/remove/move nodes around the tree. 
        Pass None to remove it from the tree.
        
        Args:
            value: The new parent node for this node.
        """
        parent = self.__parent
        if parent is not value:
            self.__detach(parent)
            self.__attach(value)
            # If a loop exists, there will be no root and the following line will throw an error
            self.root
    

    @parent.deleter
    def parent(self):
        """ Sets this parents node to None. """
        self.parent = None


    def __detach(self, parent: object):
        """ Removes this node from the old parent's children by rebuilding the children array. 
        
        Args:
            parent: The old parent node of this node.
        """
        if parent is not None:
            parentsChildren = parent.__children
            parentsChildren.remove(self)
            self.__parent = None


    def __attach(self, parent: object):
        """ Appends this node to the end of the new parent's children array. 
        
        Args:
            parent: The new parent node of this node.
        """
        if parent is not None:
            parentsChildren = parent.__children
            parentsChildren.append(self)
            self.__parent = parent


    @property
    def children(self) -> list:
        """ Returns the list of children of this node. """
        return self.__children


    @children.setter
    def children(self, children: list):
        """ Changes the children of this node, accomplished by changing each child's parent. 

        Orphaned children have their parent set to None.
        
        Args:
            children: List of children to set.
        """
        del self.children
        for child in children:
            child.parent = self


    @children.deleter
    def children(self):
        """ Removes all children of this node and sets all children's parents to None. """
        for child in reversed(self.children):
            child.parent = None


    @property
    def root(self) -> object:
        """ Returns the root node of the tree. """
        node = self
        while node.parent is not None:
            node = node.parent
            # Then we must have looped back to ourself and the tree has a loop
            if node == self:
                raise CircularTreeError
        return node


    @property
    def row(self) -> int:
        """ Returns the index of this node in its parent's children list. 

        Returns None if the node is the root.
        """
        parent = self.__parent
        if self.isRoot():
            return None
        parentsChildren = parent.__children
        return parentsChildren.index(self)


    @row.setter
    def row(self, value: int):
        """ Moves this node to a given index within its parent's children list. 
        
        Args:
            value: New index for the node in its parent's children
        """
        if self.__parent is not None:
            parent = self.__parent
            parentsChildren = parent.__children
            parentsChildren.remove(self)
            parentsChildren.insert(value, self)


    def isRoot(self) -> bool:
        """ Returns if this node is the root node. """
        return self.parent is None
    

    def numChildren(self) -> int:
        """ Returns the number of children this node has. """
        return len(self.__children)
    

    def nextSibling(self) -> object:
        """ Returns the next sibling of this node. 
        
        If this node is the last child of its parent, then it will return the first child.
        If this node is the root node, returns None.
        """
        if self.isRoot():
            return None
        index = (self.row + 1) % self.parent.numChildren()
        return self.parent.children[index]
    

    def __iter__(self):
        """ Iterates through this node's children. """
        return iter(self.__children)
    

    def iterSubTree(self) -> object:
        """ Iterates through the subtree with this node as the root in depth first order."""
        yield self
        for c in self:
            yield from c.iterSubTree()


class CircularTreeError(Exception):
    def __init__(self, message="Setting this parent or child would create a circular tree"):
        super().__init__(message)
