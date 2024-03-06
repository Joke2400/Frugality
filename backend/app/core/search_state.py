from enum import Enum


class SearchState(str, Enum):
    """Enum for representing the state of a search."""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PARSE_ERROR = "PARSE_ERROR"
    NO_RESPONSE = "NO_RESPONSE"
