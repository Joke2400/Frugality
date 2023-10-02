from abc import ABC, abstractmethod


class State(ABC):
    """Singleton base-class for representing states.

    Subsequent calls of State() constructor thus
    return the same instance as the very first call.
    Subclassing State return creates a new singleton
    with the same functionality.
    """

    def __new__(cls):
        """State singleton for representing a state."""
        if not hasattr(cls, "_state"):
            state = super(State, cls).__new__(cls)
            cls._state = state
        return cls._state

    @abstractmethod
    def __repr__(self) -> str:
        """__repr__ must be implemented."""


class Pending(State):
    """State singleton for representing 'Pending' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <Pending>"


class Success(State):
    """State singleton for representing 'Success' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <Success>"


class Fail(State):
    """State singleton for representing 'Fail' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <Fail>"


class ParseFailed(State):
    """State singleton for representing 'ParseFailed' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <ParseFailed>"


class NoResponse(State):
    """State singleton for representing 'NoResponse' state."""

    def __repr__(self) -> str:
        """Return state representation as a string."""
        return "State: <NoResponse>"
