"Contains the SearchContext ctx manager used in the app search flows."
import time
from typing import Type, TypeVar, Generic, Any, Self, Tuple, cast
from fastapi import BackgroundTasks, HTTPException

from app.core import typedefs
from app.core.orm import schemas, operations
from app.core.search.store_flow import APIStoreSearchStrategy
from app.core.search.product_flow import APIProductSearchStrategy
from app.core.search.state import SearchState

from app.utils.patterns import Strategy
from app.utils.util_funcs import assert_never
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=Strategy)

QueryT = schemas.StoreQuery | list[typedefs.ProductQueryDictT]


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
    _last_result: Tuple[SearchState, Any]

    __slots__ = "_strategy", "_background_tasks", "_last_result"

    def __init__(
            self, background_tasks: BackgroundTasks,
            strategy: StrategyT | None = None) -> None:
        self._background_tasks = background_tasks
        self.strategy = strategy

    @property
    def strategy(self) -> StrategyT | None:
        """Strategy property getter."""
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: Any) -> None:
        """Strategy property setter."""
        if not isinstance(new_strategy, Strategy):
            self._strategy = new_strategy
        else:
            raise ValueError(
                "New Strategy must be instance of patterns.Strategy.")

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
        self._last_result = await self.strategy.execute(
            *args, user_query=user_query,
            background_tasks=self._background_tasks, **kwargs)
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        logger.info("%s Took %.2fms to execute.", self.strategy, duration)
        state, data = self._last_result
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
            exc_value: Any,
            traceback: Any
            ):
        logger.debug("Exiting SearchContext(strategy=%s)", self.strategy)
        # Catch possible exceptions here ...
        if exc_type is not None:
            if exc_type is HTTPException:
                return False
            logger.error(
                "An exception occurred.",
                exc_info=(exc_type, exc_value, traceback))
            raise HTTPException(
                detail="Internal Server Error",
                status_code=500
            )
        match self.strategy:
            case APIStoreSearchStrategy():
                items = cast(list[schemas.Store], self._last_result[1])
                self._background_tasks.add_task(
                    operations.save_stores, items=items)
            case APIProductSearchStrategy():
                pass
            case _:
                pass
        return False
