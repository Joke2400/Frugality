from functools import wraps
import time
import re


def timer(func):
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
    if len(result) > 0:
        return result
    return None
