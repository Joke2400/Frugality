"Contains the SearchContext ctx manager used in the app search flows."
from typing import TypeVar, Generic, Any, Self, cast
from fastapi import BackgroundTasks, HTTPException

from backend.app.core import tasks
from backend.app.core.store_search import (
    DBStoreSearchStrategy,
    APIStoreSearchStrategy
)
from backend.app.core.product_search import (
    DBProductSearchStrategy,
    APIProductSearchStrategy
)
from backend.app.core.typedefs import (
    StoreSearchResult,
    ProductSearchResult
)
from backend.app.core.search_state import SearchState
from backend.app.core.orm import schemas

from backend.app.utils.patterns import Strategy
from backend.app.utils.util_funcs import assert_never
from backend.app.utils.exceptions import ResourceNotInDBException
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=Strategy)

QueryT = schemas.StoreQuery | schemas.ProductQuery

ResultT = StoreSearchResult | ProductSearchResult


class SearchContext(Generic[StrategyT]):
    """Context manager for managing the search flow.

    Returns successful requests, raises HTTPExceptions upon failure &
    sets up background tasks to be run by FastAPI post-search.
    """
    query: QueryT
    result: ResultT
    strategy: StrategyT
    task: BackgroundTasks

    __slots__ = "query", "strategy", "task", "result"

    def __init__(self, query: QueryT,
                 strategy: StrategyT, task: BackgroundTasks) -> None:
        self.query = query
        self.strategy = strategy
        self.task = task

    async def execute_strategy(
            self, *args: Any, **kwargs: Any) -> list | dict:
        """Execute the current strategy.

        Args:
            Passed in args & kwargs are passed onto the execute method
            defined by the current strategy. self.query is also always
            passed into the method as a keyword argument.
        Raises:
            HTTPException 500:
                Raised if no response was received from the external api. 
                Also raised if an error occurred when parsing the response.
            HTTPException 404:
                Raised if both the DB and API searches yielded no results.
            ResourceNotInDBException:
                Raised if the database search yields no results.
                Is immediately suppressed by the __exit__ method so
                that an API search may still be run afterwards.
        Returns:
            Returns either a list or a dict depending on the return value
            of the current strategy. 
            See typedefs StoreSearchResult & ProductSearchResult
        """
        # Cast result to ResultT so that mypy 'knows' it's not 'Any'
        self.result = cast(ResultT, await self.strategy.execute(
            *args, query=self.query, context=self, **kwargs))
        state, data = self.result
        logger.debug("Matching against %s...", state)
        match state:
            case SearchState.NO_RESPONSE:
                logger.debug('Matched: SearchState.NO_RESPONSE')
                raise HTTPException(
                    detail="Got no response from external API.",
                    status_code=500
                )
            case SearchState.PARSE_ERROR:
                logger.debug('Matched: SearchState.PARSE_ERROR')
                raise HTTPException(
                    detail="Could not parse results from external API.",
                    status_code=500
                )
            case SearchState.FAIL:
                logger.debug('Matched: SearchState.FAIL')
                if isinstance(
                        self.strategy,
                        (DBStoreSearchStrategy,
                         DBProductSearchStrategy)):
                    raise ResourceNotInDBException()
                raise HTTPException(
                    detail="Could not find any results for the query.",
                    status_code=404)
            case SearchState.SUCCESS:
                logger.debug('Matched: SearchState.SUCCESS')
                return data
            case _ as x:
                assert_never(x)

    def __enter__(self) -> Self:
        """Logs the current strategy & query before entering the context."""
        logger.info(
            "Performing a new search using %s", self.strategy)
        logger.debug(
            "Searching for results using query: %s", self.query)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the context & call background tasks.

        If a ResourceNotInDBException was raised, suppress it.
        Any other exceptions are re-raised (context returns false.)

        If no exceptions were raised & SearchState is SUCCESS:
            -> Calls background tasks to save the results to the DB.
        """
        # Instantly suppress this as we still want to run the API
        # search before yielding a 404-status code to the end-user
        if exc_type is ResourceNotInDBException:
            return True
        if exc_type is None:
            # Call background tasks to save results
            if self.result[0] == SearchState.SUCCESS:
                if isinstance(self.strategy, APIStoreSearchStrategy):
                    # Cast to StoreResultT to help mypy type-checking
                    store_result: StoreSearchResult = cast(
                        StoreSearchResult, self.result)
                    self.task.add_task(
                        tasks.save_store_results, store_result)
                if isinstance(self.strategy, APIProductSearchStrategy):
                    # Cast to ProductResultT to help mypy type-checking
                    product_result: ProductSearchResult = cast(
                        ProductSearchResult, self.result)
                    self.task.add_task(
                        tasks.save_product_results, product_result)
        return False
