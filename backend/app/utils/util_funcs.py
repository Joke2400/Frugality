from typing import NoReturn, Never


def assert_never(args: Never) -> NoReturn:
    """This function is supposed to be unreachable.

    Raises an AssertionError when called.
    """
    raise AssertionError("Expected code is unreachable.")
