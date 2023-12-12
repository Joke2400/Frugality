"""Classes for managing the search flow."""
import asyncio
from enum import Enum
from typing import TypeVar, Generic, Any, Callable, Coroutine
from fastapi import BackgroundTasks

from app.core import parse, tasks
from app.core.orm import schemas, crud
from app.api import request
from app.api.skaupat import query as api
from app.utils.logging import LoggerManager
from app.utils import patterns, exceptions


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)
ProductSearchResultT = \
    list[
        tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]
    ]

# TODO: Refactoring pass on the already implemented strategies


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


class DBStoreSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[SearchState, list[schemas.StoreDB]]:  # TODO: Proper typehint for async
        query: str | int
        crud_func: Callable
        try:
            query = int(context.query)
            crud_func = crud.get_store_by_id
        except ValueError:
            query = str(context.query)
            crud_func = crud.get_stores_by_slug

        match crud_func(query):
            case [] | None:
                context.status = SearchState.FAIL
                logger.info("DB: Failed to find items for query '%s'.",
                            context.query)
                return context.status, []
            case list() as data:
                context.status = SearchState.SUCCESS
                logger.info("DB: Got %s results for query '%s'.",
                            len(data), context.query)
                return context.status, data
            case schemas.StoreDB() as data:
                context.status = SearchState.SUCCESS
                logger.info("DB: Got result for query '%s'.", context.query)
                return context.status, [data]
            case _ as data:
                raise ValueError(
                    f"Match stmt matched an undefined value: {data}")


class APIStoreSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[SearchState, list[schemas.Store]]:  # TODO: Proper typehint for async
        params = api.build_request_params(
            method="post",
            operation=api.Operation.STORE_SEARCH,
            variables=api.build_store_search_vars(
                str(context.query)),
            timeout=10)
        logger.debug("Awaiting request for query '%s'", context.query)
        response = await request.send_request(params=params)
        if response is None:
            context.status = SearchState.NO_RESPONSE
            logger.error(
                "Received no API response to parse.")
            return context.status, []

        logger.debug("Parsing response for query '%s'", context.query)
        match parse.parse_store_response(response, str(context.query)):
            case None:
                context.status = SearchState.PARSE_ERROR
                logger.error("Could not parse stores from API response.")
                return context.status, []
            case []:
                context.status = SearchState.FAIL
                logger.info(
                    "API: Failed to find items for query '%s'.",
                    context.query)
                return context.status, []
            case list() as data:
                logger.info("API: Got %s results for query '%s'.",
                            len(data), context.query)
                context.status = SearchState.SUCCESS
                context.background_tasks.add_task(
                    tasks.save_store_results, stores=data)
                return context.status, data
            case _ as data:
                raise exceptions.InvalidMatchCaseError(
                    f"Could not match value: {data} to a predefined case.")


class DBProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(context: SearchContext) -> None:
        # TODO: This function
        pass


class APIProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[ProductSearchResultT, ProductSearchResultT]:
        async_tasks = []
        user_query: schemas.ProductQuery = context.query
        for store_id in user_query.stores:
            for query in user_query.queries:
                params = api.build_request_params(
                    method="post",
                    operation=api.Operation.PRODUCT_SEARCH,
                    variables=api.build_product_search_vars(
                        store_id=store_id, query=query),
                    timeout=10)
                logger.debug(
                    "Creating task for: (store_id: %s, query: %s)",
                    store_id, query)
                async_tasks.append(asyncio.create_task(
                    api.send_product_query(query=query, params=params)))
        results = await asyncio.gather(*async_tasks)
        successful_queries = []
        failed_queries = []
        for result in results:
            if len(result) == 0:
                failed_queries.append(result)
            else:
                successful_queries.append(result)
        context.background_tasks.add_task(
            tasks.save_product_results, results=successful_queries)
        return successful_queries, failed_queries
