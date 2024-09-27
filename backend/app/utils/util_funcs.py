"""Contains utility functions used for tests, debugging etc."""

import os
import time
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
            f"The required environment variable '{key}' was missing."
        )
    return str(var)


def cleanup(func: Callable[..., None]) -> Callable[..., None]:
    """A cleanup decorator that purges the database after function call."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func(*args, **kwargs)
        logger.debug("Cleanup wrapper is resetting the database...")
        ORM().purge_all()
        ORM().create_all()

    return wrapper


def build_db_url(usr: str, passwd: str, db: str, testing: bool) -> str:
    """Build a database connect URL."""
    auth: str = f"{usr}:{passwd}"
    if not testing:
        host: str = f"frugality_database/{db}"
    else:
        host = "localhost:5433/test_database"
    logger.info(f"Set postgres host to @{host}")
    return f"postgresql://{auth}@{host}"


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """A timer decorator."""

    def wrapper(*args: Any, **kwargs: Any):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        print(f"Function '{func.__name__}()' took {elapsed_time:.2f}ms")
        return result

    return wrapper
