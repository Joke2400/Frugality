from abc import ABC, abstractmethod


class State(ABC):
    """Singleton base-class for representing states.

    Subsequent calls of State() constructor thus
    return the same instance as the very first call.
    Subclassing State return creates a new singleton
    with the same functionality.
    """

    def __new__(cls):
        """Implement singleton-pattern for class.

        If an instance of state does not exist, create a new instance.
        If it already exists, return that one. Only one instance of
        the class may exist at a time.
        """
        if not hasattr(cls, "_state"):
            state = super(State, cls).__new__(cls)
            cls._state = state
        return cls._state

    @abstractmethod
    def __repr__(self) -> str:
        """__repr__ must be implemented."""


class Found(State):
    """State singleton for representing 'Found' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <Found>"


class NotFound(State):
    """State singleton for representing 'NotFound' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <NotFound>"


class ParseFailed(State):
    """State singleton for representing 'ParseFailed' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <ParseError>"
