
from enum import Enum
from typing import TypeVar, Generic, Any, Self, Coroutine
from fastapi import BackgroundTasks

from backend.app.core.orm import schemas
from backend.app.utils import patterns
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)

# is also defined in typedefs.py, redefined here to avoid circular import
QueryType = schemas.StoreQuery | schemas.ProductQuery


class DBSearchState(str, Enum):
    """Enum for representing the state of a DB search.

    Used in both the search functions as well as
    the route match-case statements.
    """
    SUCCESS = "DB_SUCCESS"
    FAIL = "DB_FAIL"


class APISearchState(str, Enum):
    """Enum for representing the state of an API search.

    Used in both the search functions as well as
    the route match-case statements.
    """
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PARSE_ERROR = "PARSE_ERROR"
    NO_RESPONSE = "NO_RESPONSE"


class SearchContext(Generic[StrategyT]):
    """Context manager class for managing searches.

    Used for both store and product searches.
    Is intended to initiate the background task given upon exit.
    (but not implemented now.)
    """

    # Using predefined query formats from schemas.py
    query: QueryType
    strategy: StrategyT
    task: BackgroundTasks

    __slots__ = "query", "strategy", "task"

    def __init__(self, query: QueryType,
                 strategy: StrategyT, task: BackgroundTasks) -> None:
        self.query = query
        self.strategy = strategy
        self.task = task

    async def execute_strategy(self, *args: Any, **kwargs: Any) -> Coroutine:  # TODO: Remember to make this hint more specific
        """Execute the current strategy with the given set of args & kwargs"""
        return await self.strategy.execute(
            *args, query=self.query, context=self, **kwargs)

    def __enter__(self) -> Self:
        logger.debug(f"Starting new search using: {self.strategy} ")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        # Code calling additional background tasks will be here in the future
        # For example -> background tasks for pagination
        # there are around 800-900 s-ryhmä stores so:
        # Check cursor location vs total length from API upon return of the
        # awaited strategy, then after returning result to user -> queue background
        # task here to paginate API results -> should result in backend fetching
        # all stores when querying for just the brand (ex. 'prisma')
        return True
