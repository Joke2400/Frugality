"""Contains custom exception classes."""


class FrugalityError(Exception):
    """Exception base-class for exceptions raised by Frugality."""

    def __init__(self, message: str = "Service is unavailable.",
                 name: str = "Frugality") -> None:
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class MissingEnvironmentVariableError(FrugalityError):
    """A required environment variable was not provided."""


class MissingResourceError(FrugalityError):
    """Raised when a resource is not found in the database."""


class UnknownPathError(FrugalityError):
    """Raised when a project path could not be determined."""
