"Contains the SearchContext ctx manager used in the app search flows."
import time
from typing import Type, TypeVar, Generic, Any, Self, Tuple
from fastapi import BackgroundTasks, HTTPException

from app.core import tasks
from app.core.search.store_flow import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from app.core.search.product_flow import (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)
from app.core.search.state import SearchState
from app.core.orm import schemas

from app.utils.patterns import Strategy
from app.utils.util_funcs import assert_never
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=Strategy)

QueryT = schemas.StoreQuery | schemas.ProductQuery


class SearchContext(Generic[StrategyT]):
    """A SearchContext to serve as the context for search strategies.

    Args:
        background_tasks (BackgroundTasks):
            Required, a FastAPI.BackgroundTasks must be provided.
        strategy (StrategyT | None):
            Can be provided on initialization, but has to have been
            set before call to 'execute()'.
    """
    _strategy: StrategyT | None
    _background_tasks: BackgroundTasks

    __slots__ = "_strategy", "_background_tasks"

    def __init__(
            self, background_tasks: BackgroundTasks,
            strategy: StrategyT | None = None) -> None:
        self._background_tasks = background_tasks
        self._strategy = strategy

    @property
    def strategy(self) -> StrategyT | None:
        """Strategy property getter."""
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: StrategyT) -> None:
        """Strategy property setter."""
        if not isinstance(new_strategy, Strategy):
            raise ValueError(
                "New Strategy must be instance of patterns.Strategy.")
        self._strategy = new_strategy

    async def execute(
            self, user_query: QueryT, *args: Any, **kwargs: Any
            ) -> tuple[SearchState, Any]:
        """Execute the current strategy with the provided user query.

        Args:
            user_query (QueryT): Either a StoreQuery or ProductQuery
            Any other *args or **kwargs given will be passed into the strategy

        Raises:
            HTTPException(500):
                Raised if request state is NO_RESPONSE or PARSE_ERROR
                or if some other error occurred during search.

        Returns:
            tuple[SearchState, Any]:
                Returns the SearchState and result data as a tuple.
        """
        if self.strategy is None:
            raise ValueError(
                "A search strategy was not set before call to execute().")
        start_time = time.time()
        result: Tuple[SearchState, Any] = await self.strategy.execute(
            *args, query=user_query, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        logger.info("%s Took %.2fms to execute.", self.strategy, duration)
        state, data = result
        # Match against the state variable in the returned tuple
        # Nested parts of query may have a different SearchState
        # Responsibility of handling this is on the calling route
        match state:
            case SearchState.NO_RESPONSE | SearchState.PARSE_ERROR:
                raise HTTPException(
                    detail="Internal Server Error",
                    status_code=500
                )
            case SearchState.SUCCESS | SearchState.FAIL \
                    | SearchState.PARTIAL_RESULT:
                return state, data
            case _ as x:  # type: ignore
                assert_never(x)

    def __enter__(self) -> Self:
        logger.debug("Entering SearchContext(strategy=%s)", self.strategy)
        return self

    def __exit__(
            self, exc_type: Type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: Type[BaseException] | None
            ):
        logger.debug("Exiting SearchContext(strategy=%s)", self.strategy)
        # Catch possible exceptions here ...
        if exc_type is not None:
            if exc_type is HTTPException:
                return False
            raise HTTPException(
                detail="Internal Server Error",
                status_code=500
            )
        # Call background tasks to save results.
        logger.debug(
            "Appending tasks to 'BackgroundTasks' to save query results.")
        return False
