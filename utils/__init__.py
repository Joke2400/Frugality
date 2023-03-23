"""Contains various utility functions and classes."""

from .program_paths import Paths
from .logger_manager import LoggerManager

# Cant be moved lower yet because LoggerManager needs a logic change
LoggerManager.configure(logs_path=Paths.logs(), keep_logs=False)
logger = LoggerManager.get_logger(name=__name__, stream=True)

from .util_funcs import timer
from .util_funcs import regex_search
from .util_funcs import regex_findall
from .util_funcs import get_quantity_from_string

__all__ = ["Paths", "LoggerManager", "timer",
           "regex_search", "regex_findall",
           "get_quantity_from_string"]
