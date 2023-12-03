"""Classes for managing the search flow."""
from enum import Enum
from typing import TypeVar, Generic, Any, Callable

from app.core import parse
from app.core.orm import schemas, crud
from app.api import request
from app.api.skaupat import query as api_query
from app.utils.logging import LoggerManager
from app.utils import patterns, exceptions


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)


class State(str, Enum):
    """TODO: DOCSTRING"""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    PENDING = "PENDING"

    PARSE_ERROR = "PARSE_ERROR"
    NO_RESPONSE = "NO_RESPONSE"


class SearchContext(patterns.StrategyContext, Generic[StrategyT]):
    """TODO: DOCSTRING"""
    query: Any
    strategy: StrategyT
    status: State

    __slots__ = "query", "strategy", "status"

    def __init__(self, strategy: StrategyT):
        super().__init__(strategy=strategy)
        self.status = State.PENDING

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the search strategy with provided query.

        # TODO: Figure out a better solution than *args & **kwargs
        # linter complains about the function signature
        # if I don't use them here.
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
            ) -> tuple[State, list[schemas.StoreDB]]:
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


class APIStoreNameSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[State, list[schemas.Store]]:
        params = api_query.build_request_params(
            method="post",
            operation=api_query.Operation.STORE_SEARCH,
            variables=api_query.build_store_search_variables(
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
        match parse.parse_store_response(response):
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
# TODO: Refactor DB/API strategy to be more generic
# Or split the match statement into an external function
# & create several smaller strategies