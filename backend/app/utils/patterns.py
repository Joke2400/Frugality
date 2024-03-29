"""Python implementations for standard design patterns."""
from abc import ABC, abstractmethod
from typing import (
    TypeVar,
    Any,
    Generic,
)
from typing_extensions import Self

StrategyT = TypeVar("StrategyT", bound="Strategy")
StrategyContextT = TypeVar("StrategyContextT", bound="StrategyContext")


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

    @classmethod
    def _debug_clear(cls):
        """Clear the instances dict."""
        cls._instances = {}


T = TypeVar("T")


class TreeNode(Generic[T]):
    """A Node class representing a single element in a tree data structure."""

    def __init__(self, data: T) -> None:
        """Initialize node with data."""
        self.data: Any = data
        self.children: list[TreeNode[T]] = []
        self.parent: TreeNode[T] | None = None

    def add_child(self, child: Self) -> None:
        """Add a child to this node. Set child parent to this node."""
        child.parent = self
        self.children.append(child)


class StrategyContext(ABC, Generic[StrategyT]):
    """An ABC for a context class that executes strategies."""
    strategy: StrategyT

    def __init__(self, strategy: StrategyT) -> None:
        self.strategy = strategy

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any):
        """Implement this abstractmethod when inheriting."""


class Strategy(ABC, Generic[StrategyContextT]):
    """ABC for a strategy pattern."""

    @staticmethod
    @abstractmethod
    async def execute(context: StrategyContextT):
        """Implement this abstractmethod when inheriting."""

    @classmethod
    def __repr__(cls) -> str:
        return f"<{cls.__name__}>"
