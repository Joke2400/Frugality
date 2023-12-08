"""Classes for managing the search flow."""
import asyncio
from enum import Enum
from typing import TypeVar, Generic, Any, Callable, Coroutine

from app.core import parse
from app.core.orm import schemas, crud
from app.api import request
from app.api.skaupat import query as api
from app.utils.logging import LoggerManager
from app.utils import patterns, exceptions


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)


class State(str, Enum):
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
    strategy: StrategyT
    status: State

    __slots__ = "query", "strategy", "status"

    def __init__(self, strategy: StrategyT):
        super().__init__(strategy=strategy)
        self.status = State.PENDING

    async def execute(self, *args: Any, **kwargs: Any
                      ) -> Coroutine[Any, Any, None]:  # TODO: Proper typehint for async
        """Execute the current search strategy with the provided query.
        Args:
            query (Any): a 'query' keyword argument must be provided.

        Returns:
            Any: _description_
        """
        query: Any = kwargs["query"]
        logger.debug(
            "Executing strategy '%s' with query '%s'",
            self.strategy, query)
        self.query = query
        return await self.strategy.execute(context=self)


class DBStoreSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[State, list[schemas.StoreDB]]:  # TODO: Proper typehint for async
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
                context.status = State.FAIL
                logger.info("DB: Failed to find items for query '%s'.",
                            context.query)
                return context.status, []
            case list() as data:
                context.status = State.SUCCESS
                logger.info("DB: Got %s results for query '%s'.",
                            len(data), context.query)
                return context.status, data
            case schemas.StoreDB() as data:
                context.status = State.SUCCESS
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
            ) -> tuple[State, list[schemas.Store]]:  # TODO: Proper typehint for async
        params = api.build_request_params(
            method="post",
            operation=api.Operation.STORE_SEARCH,
            variables=api.build_store_search_vars(
                str(context.query)),
            timeout=10)
        logger.debug("Awaiting request for query '%s'", context.query)
        response = await request.send_request(params=params)
        if response is None:
            context.status = State.NO_RESPONSE
            logger.error(
                "Received no API response to parse.")
            return context.status, []

        logger.debug("Parsing response for query '%s'", context.query)
        match parse.parse_store_response(response, str(context.query)):
            case None:
                context.status = State.PARSE_ERROR
                logger.error("Could not parse stores from API response.")
                return context.status, []
            case []:
                context.status = State.FAIL
                logger.info(
                    "API: Failed to find items for query '%s'.",
                    context.query)
                return context.status, []
            case list() as data:
                logger.info("API: Got %s results for query '%s'.",
                            len(data), context.query)
                context.status = State.SUCCESS
                return context.status, data
            case _ as data:
                raise exceptions.InvalidMatchCaseError(
                    f"Could not match value: {data} to a predefined case.")


class DBProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(context: SearchContext) -> None:
        pass


class APIProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(context: SearchContext) -> None:
        tasks = []
        user_query: schemas.ProductQuery = context.query
        for store_id in user_query.stores:
            for item_query in user_query.queries:
                query: dict[str, str | int] = {
                    "store_id": store_id,
                    "query": item_query["query"],
                    "slugs": item_query["category"]
                }
                params = api.build_request_params(
                    method="post",
                    operation=api.Operation.PRODUCT_SEARCH,
                    variables=api.build_product_search_vars(query=query),
                    timeout=10)
                logger.debug(
                    "Creating async task for: (store_id: '%s', query: '%s')",
                    store_id, item_query)
                tasks.append(asyncio.create_task(
                    api.send_product_query(query=query, params=params)))
        results = await asyncio.gather(*tasks)
        print("Length of results: ", len(results))
