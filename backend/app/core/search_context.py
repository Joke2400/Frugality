
from enum import Enum
from typing import TypeVar, Generic, Any, Coroutine
from fastapi import BackgroundTasks

from backend.app.utils import patterns
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)


class SearchState(str, Enum):
    """Enum for representing the state of a search."""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PENDING = "PENDING"
    PARSE_ERROR = "PARSE_ERROR"
    NO_RESPONSE = "NO_RESPONSE"


class SearchContext(patterns.StrategyContext, Generic[StrategyT]):
    """Context for executing a search strategy.

    Inherits from patterns.StrategyContext ABC & implements execute().
    """
    # TODO: Look into changing query variable
    # TODO: self.execute() *args **kwargs is too unspecific,
    # hard to know what exactly the function expects as an argument.
    query: Any
    background_tasks: BackgroundTasks
    strategy: StrategyT
    status: SearchState

    __slots__ = "query", "strategy", "status"

    def __init__(self, strategy: StrategyT):
        super().__init__(strategy=strategy)
        self.status = SearchState.PENDING

    async def execute(self, *args: Any, **kwargs: Any
                      ) -> Coroutine[Any, Any, None]:  # TODO: Proper typehint for async
        """Execute the current search strategy with the provided query.
        Args:
            query (Any): a 'query' keyword argument must be provided.
            tasks (BackgroundTasks):
            A 'tasks' keyword argument must be provided.

        # TODO: Improve this docstring....
        Returns:
            Any: _description_
        """
        query: Any = kwargs["query"]
        background_tasks: BackgroundTasks = kwargs["tasks"]
        logger.debug(
            "Executing strategy %s with query %s",
            self.strategy, query)
        self.query = query
        self.background_tasks = background_tasks
        return await self.strategy.execute(context=self)
