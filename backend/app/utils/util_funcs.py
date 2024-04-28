import os
from typing import NoReturn, Never, Any, Callable
from app.core.orm.database import ORM
from app.utils import exceptions
from app.utils import LoggerManager

logger = LoggerManager().get_logger(__name__, sh=0, fh=10)


def assert_never(args: Never) -> NoReturn:
    """This function is supposed to be unreachable.

    Raises an AssertionError when called.
    """
    raise AssertionError("Expected code is unreachable.")


def get_envvar(key: str) -> str:
    """Get an environment variable.
    Args:
        key (str): The key to fetch.

    Raises:
        exceptions.MissingEnvironmentVar:
            Raised if the environment variable was not found.

    Returns:
        str: Always returns the found variable as a string
    """
    if (var := os.getenv(key=key)) in ("", None):
        raise exceptions.MissingEnvironmentVariableError(
            f"The required environment variable '{key}' was missing.")
    return str(var)


def cleanup(func: Callable[..., None]) -> Callable[..., None]:
    """A cleanup decorator that purges the database after function call."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func(*args, **kwargs)
        logger.debug("Cleanup wrapper is resetting the database...")
        ORM().purge_all()
        ORM().create_all()
    return wrapper


def log_func_name(func: Callable[..., None]) -> Callable[..., None]:
    """Decorator that logs the function name."""
    def wrapper(*args, **kwargs):
        logger.debug("Running test: %s()", func.__name__)
        return func(*args, **kwargs)
    return wrapper
