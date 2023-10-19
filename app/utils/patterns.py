from abc import ABC, abstractmethod
from typing import TypeVar, Type, TypeAlias, Any


class Validator(ABC):
    """A validator descriptor for managed attribute access.

    This validator descriptor is specified in:
    https://docs.python.org/3/howto/descriptor.html#validator-class
    """

    private_name: str

    def __set_name__(self, owner, name):
        """Save managed attribute private name in descriptor instance."""
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        """Call getattr on object using stored private name."""
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        """Call setattr after calling abstract validation function."""
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        """Abstract validation function that needs to be implemented."""


class OneOfType(Validator):
    """Validator that ensures that input value is of a valid type."""

    def __init__(self, *options):
        """Initialize validator with a set of types that are valid."""
        self.options = set(options)

    def validate(self, value):
        """Check that input value is of a type supplied in call to init."""
        is_valid_type = False
        for i in self.options:
            if isinstance(value, i):
                is_valid_type = True
                break
        if not is_valid_type:
            raise ValueError(
                f'Expected {value!r} to be one of {self.options!r}')


class SingletonMeta(type):
    """Metaclass that implements a singleton pattern by overriding __call__."""

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        """Return the same instance of a class upon subsequent calls.

        Instances are stored as a class dict '_instances'.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


_TreeNode = TypeVar("_TreeNode", bound="TreeNode")
_TreeRoot = TypeVar("_TreeRoot", bound="TreeRoot")
_Node: TypeAlias = _TreeNode | _TreeRoot


class TreeRoot:
    """The root node of a tree datastructure."""

    def __init__(self, data: Any) -> None:
        """Initialize the root of the tree."""
        self.data: Any = data
        self.children: list[_Node] = []

    def add_child(self, child: _TreeNode) -> None:
        """Add a child to this node, and set its parent to this node."""
        self.children.append(child)
        child.set_parent(parent=self)

    def get_children(self) -> list[_TreeNode]:
        """Return a list of child nodes."""
        return self.children


class TreeNode(TreeRoot):
    """A node in the tree datastructure.

    Note: The constructor does not take in a parent node.
    This must be added manually by calling set_parent()
    """

    def __init__(self, data: Any) -> None:
        """Initialize a node in the tree."""
        super().__init__(data)
        self.parent: Type[_Node]

    def set_parent(self, parent: _Node) -> None:
        """Set the parent of this node."""
        self.parent = parent

    def get_parent(self) -> Type[_TreeNode]:
        """Get the parent of this node."""
        return self.parent
