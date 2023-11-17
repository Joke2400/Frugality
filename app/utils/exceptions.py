"""Contains custom exception classes."""


class CustomErrorBase(Exception):
    """Custom error base class."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class MissingEnvironmentVar(CustomErrorBase):
    """A required environment variable was not provided."""
