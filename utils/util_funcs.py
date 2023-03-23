import time
import re
from functools import wraps

from .logger_manager import LoggerManager

logger = LoggerManager.get_logger(name=__name__)


def timer(func):
    """Time the execution of a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"Function: [{func.__name__}] Took: {1000*elapsed:.0f}ms")
        return result
    return wrapper


def regex_search(pattern: str, string: str
                 ) -> re.Match[str] | None:
    """Scan through a string and return a single RegEx match.

    Returns a Match object if a match is found,
    returns None in other cases.

    Args:
        pattern (str): RegEx pattern as a raw string.
        string (str): String to be matched against

    Returns:
        re.Match[str] | None: Returns either a Match object or None
    """
    result = re.search(
        pattern=pattern,
        string=string,
        flags=re.I | re.M)
    logger.debug("regex_search() -> %s", result)
    return result


def regex_findall(pattern: str, string: str
                  ) -> list | None:
    """Scan through a string and return multiple RegEx matches.

    Args:
        pattern (str): RegEx pattern as a raw string.
        string (str): String to be matched against

    Returns:
        list | None: Returns either a list, or None if there
        were no matches to pattern.
    """
    result = re.findall(
        pattern=pattern,
        string=string,
        flags=re.I | re.M)
    logger.debug("regex_findall() -> %s", result)
    if len(result) > 0:
        return result
    return None


def get_quantity_from_string(string: str) -> tuple[int | float, str] | None:
    """Get a quantity from a given string.

    Returns a tuple containing the quantity as an integer or float.
    And the unit of the extracted quantity as a string.
    Units are ex: l, dl, cl, ml, kg, g, mg

    Args:
        string (str): String to be matched against.

    Returns:
        tuple[int | float, str] | None: Returns either a float or int
        depending on regex capture results. If no match is found,
        returns None.
    """
    result = regex_search(
        r"((\d+[\.?,?]\d+)\s?|(\d+)\s?)(?=(l|dl|cl|ml|kg|g|mg))", string)
    if result is not None:
        try:
            # First capturing group is not used
            # If second group has a value, quantity is a decimal value
            if val := result.group(2):
                return (float(val.replace(",", ".")), result.group(4))

            # If third has a value, quantity is an integer value
            if val := result.group(3):
                return (int(val), result.group(4))
            return None

        except ValueError:
            logger.exception("Could not convert to int: %s", result[0])
    logger.debug("Could not extract quantity from string: %s", string)
    return None
