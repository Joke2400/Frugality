"""Contains custom exception classes."""


class MissingEnvironmentVar(Exception):
    """A required environment variable was not provided."""


class ExceptionInContext(Exception):
    """An exception occurred within the context of a context manager."""


class UndefinedMatchCaseError(Exception):
    """Pattern matching did not have a defined case for the value."""