"""Contains various utility functions and classes."""

from .program_paths import Paths
from .logger_manager import LoggerManager
from .util_funcs import timer
from .util_funcs import regex_search
from .util_funcs import regex_findall

LoggerManager.configure(
    logs_path=Paths.logs(),
    keep_logs=False
)

__all__ = ["Paths", "LoggerManager", "timer",
           "regex_search", "regex_findall"]
