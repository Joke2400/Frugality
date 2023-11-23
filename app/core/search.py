
"""Classes for managing the search flow."""
from enum import Enum
from typing import TypeVar, Generic, Any, Type

from app.core import parse
from app.core.orm import schemas
from app.api import request
from app.api.skaupat import query as api_query
from app.utils.logging import LoggerManager
from app.utils import patterns


logger = LoggerManager().get_logger(path=__name__, sh=20, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy, covariant=True)
SchemaT = schemas.StoreQuery


class State(str, Enum):
    """TODO: DOCSTRING"""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

    PENDING = "PENDING"
    NOT_STARTED = "NOT_STARTED"
    PARSE_ERROR = "PARSE_ERROR"
    NO_RESPONSE = "NO_RESPONSE"


class SearchContext(patterns.StrategyContext, Generic[StrategyT]):
    """TODO: DOCSTRING"""
    query: SchemaT
    strategy: StrategyT
    status: State

    __slots__ = "query", "strategy", "status"

    def __init__(self, strategy: StrategyT):
        super().__init__(strategy=strategy)
        self.status = State.NOT_STARTED

    async def execute(self, *args: Any, **kwargs: Any) -> dict:
        """Execute the search strategy with provided query.

        # TODO: Figure out a better solution than *args & **kwargs
        # linter complains about the function signature
        # if I don't use them here.
        """
        query: schemas.StoreQuery = kwargs["query"]
        self.status = State.PENDING
        logger.debug(
            "Executing strategy %s with query %s",
            self.strategy, query)
        self.query = query
        return await self.strategy.execute(context=self)


class APIStoreNameSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[State, list[schemas.StoreIn], str]:
        store_name: str = str(context.query.store_name)
        params = api_query.build_request_params(
            method="post",
            operation=api_query.Operation.STORE_SEARCH,
            variables=api_query.build_store_search_variables(store_name),
            timeout=10)
        logger.debug("Awaiting request for query %s", context.query)
        response = await request.send_request(params=params)
        logger.debug("Parsing response for query %s", context.query)
        if response is None:
            logger.debug(
                "Exception occurred during request, got no response to parse.")
            context.status = State.NO_RESPONSE
            return (
                context.status, [],
                "Unable to communicate with external API.")

        match parse.parse_store_response(response):
            case None:
                context.status = State.PARSE_ERROR
                return (
                    context.status, [],
                    "Could not parse the query from external API response.")
            case []:
                context.status = State.FAIL
                return (
                    context.status, [],
                    "Failed to find matching results for the query.")
            case list() as data:
                context.status = State.SUCCESS
                return context.status, data, "Success!"
            case _ as data:
                raise ValueError(
                    f"Parsing returned an unexpected value: {data}")


class DBStoreNameSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(context: ):
        return None
