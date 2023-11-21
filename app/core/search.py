
"""Classes for managing the search flow."""
from dataclasses import dataclass
from pydantic import BaseModel

from app.utils.patterns import AbstractStrategy
from app.utils.state import Success, Fail, Pending, ParseFailed, NoResponse

StateT = Success | Fail | Pending | ParseFailed | NoResponse


class DBSearchStrategy(AbstractStrategy):

    def execute(self):
        return None


class APISearchStrategy(AbstractStrategy):

    def execute(self):
        return None


@dataclass
class Search:
    query: BaseModel
    strategy: AbstractStrategy
    status: StateT
