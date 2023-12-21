"""Contains custom exception classes."""


class CustomErrorBase(Exception):
    """Custom error base class."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MissingEnvironmentVar(CustomErrorBase):
    """A required environment variable was not provided."""


class InvalidMatchCaseError(CustomErrorBase):
    """Pattern matching couldn't match the value against any of the cases."""


class ExceptionInContext(CustomErrorBase):
    """An exception occurred within the context of a context manager."""
