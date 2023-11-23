
"""Classes for managing the search flow."""
from enum import Enum
from typing import TypeVar, Generic, Any, Type

from app.core import parse
from app.api import request
from app.api.skaupat import query as api_query
from app.utils.logging import LoggerManager
from app.utils import patterns


logger = LoggerManager().get_logger(path=__name__, sh=20, fh=10)
StrategyT = TypeVar("StrategyT", bound=patterns.Strategy)


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
    query: dict
    strategy: StrategyT
    status: State

    __slots__ = "query", "strategy", "status"

    def __init__(self, strategy: Type[StrategyT]):
        super().__init__(strategy=strategy)
        self.status = State.NOT_STARTED

    async def execute(self, *args: Any, **kwargs: Any) -> dict:
        """Execute the search strategy with provided query.

        # TODO: Figure out a better solution than *args & **kwargs
        # linter complains about the function signature
        # if I don't use them here.
        """
        # Let the request fail here if kwargs is missing the key.
        query: dict = kwargs["query"]
        self.status = State.PENDING
        logger.debug(
            "Executing strategy %s with query %s",
            self.strategy, query)
        self.query = query
        return await self.strategy.execute(context=self)


class APISearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(context: SearchContext) -> dict:
        store_name: str = str(context.query["store_name"])
        params = api_query.build_request_params(
            method="post",
            operation=api_query.Operation.STORE_SEARCH,
            variables=api_query.build_store_search_variables(store_name),
            timeout=10)
        response = await request.send_request(params=params)
        match parse.parse_store_response(response=response):
            case _:
                pass
        return {}

    # -> "stores" key exists
    # -> "store" key


class DBSearchStrategy(patterns.Strategy):
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute():
        return None
