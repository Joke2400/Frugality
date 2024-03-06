"""Contains custom exception classes."""


class MissingEnvironmentVar(Exception):
    """A required environment variable was not provided."""


class ExceptionInContext(Exception):
    """An exception occurred within the context of a context manager."""


class ResourceNotInDBException(Exception):
    """Raised by SearchContext if a resource was not found in the DB."""
