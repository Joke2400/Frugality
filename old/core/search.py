"""Contains implementation of 'Search' dataclass."""

from dataclasses import dataclass, field
from typing import Any

from utils import State
from utils import OneOfType
from utils import Success
from utils import Fail
from utils import Pending
from utils import ParseFailed
from utils import NoResponse


@dataclass
class Search:
    """A class for storing query and result data."""

    query: Any = None
    result: Any = None
    feedback: str = ""
    state: Any = field(
        default=OneOfType(
            Pending,
            Success,
            Fail,
            ParseFailed,
            NoResponse),
        repr=False)

    def set_query(self, query: Any, state: State):
        """Set query to a value and update state."""
        self.query = query
        self.state = state

    def set_result(self, result: Any, state: State):
        """Set result to a value and update state."""
        self.result = result
        self.state = state
