"""Contains strategies for performing store searches."""
from typing import Any, cast
from httpx import Response

from app.api import request
from app.api import payload

from app.core import parse, typedefs
from app.core.orm import schemas
from app.core.orm import operations
from app.core.search.state import SearchState

from app.utils import patterns, LoggerManager
from app.utils.util_funcs import assert_never

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


class DBStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via the execute_strategy() method in SearchContext.
    """

    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
            ) -> typedefs.DBStoreSearchResult:
        """Perform a search on the database and return a result.

        Args:
            query (schemas.StoreQuery):
                A query of type schemas.StoreQuery is required.
                If both an id and name are provided in the StoreQuery,
                then the id is always used in the search.
        Raises:
            TypeError:
                Raised if kwarg 'query' was not provided.
        Returns:
            tuple[SearchState, list[schemas.StoreDB]]
                A tuple containing the SearchState and a list of results.
        """
        user_query: schemas.StoreQuery = kwargs["user_query"]
        result: list[typedefs.StoreDB] | typedefs.StoreDB | None
        if user_query.store_id is not None:
            result = operations.get_store_by_id(user_query.store_id)
        else:
            # Explicit cast, model validator has ensured its not 'None'
            q: str = cast(str, user_query.store_name)
            result = operations.get_stores_by_name(q)
        match result:
            case [] | None:
                logger.info(
                    "DB store search: Failed to find results for query: %s.",
                    user_query)
                return SearchState.FAIL, []
            case list() as data:
                logger.info(
                    "DB store search: Got %s results for query: %s.",
                    len(data), user_query)
                return SearchState.SUCCESS, data
            case schemas.StoreDB() as data:
                logger.info(
                    "DB store search: Got 1 results for query: %s.",
                    user_query)
                return SearchState.SUCCESS, [data]
            case _ as data:  # type: ignore
                assert_never(data)


class APIStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the API.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via the execute_strategy() method in SearchContext.
    """

    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
            ) -> typedefs.APIStoreSearchResult:
        """Perform a search on the external API and return a result.

        Args:
            query (schemas.StoreQuery):
                A query of type schemas.StoreQuery is required.
        Raises:
            TypeError:
                Raised if kwarg 'query' was not provided.
        Returns:
            tuple[SearchState, list[schemas.Store]]:
                A tuple containing the SearchState and a list of results.
        """
        user_query: schemas.StoreQuery = kwargs["user_query"]
        if (response := await cls._send_store_query(
                user_query=user_query)) is None:
            logger.error(
                "API store search: Received no API response to parse.")
            return SearchState.NO_RESPONSE, []
        parsed = parse.parse_store_response(response, user_query)
        match parsed:
            case None:
                logger.error(
                    "API store search: Failed to parse results from response.")
                return SearchState.PARSE_ERROR, []
            case []:
                logger.info(
                    "API store search: Got 0 results for query: %s.",
                    user_query)
                return SearchState.FAIL, []
            case list() as data:
                logger.info("API store search: Got %s results for query: %s.",
                            len(data), user_query)
                return SearchState.SUCCESS, data
            case _ as data:  # type: ignore
                assert_never(data)

    @staticmethod
    async def _send_store_query(
            user_query: schemas.StoreQuery
            ) -> Response | None:
        """Build API request payload and send store request.

        Args:
            query (schemas.StoreQuery):
                The store query to build the request with.

        Returns:
            Response | None:
                Either a httpx.Response or None if no response
                was received or an error occurred.
        """
        if user_query.store_id is not None:
            store_query: str = str(user_query.store_id)
        else:
            store_query = str(user_query.store_name)
        params = payload.build_request_payload(
            method="post",
            operation=payload.Operation.STORE_SEARCH,
            variables=payload.build_store_variables(store_query),
            timeout=10)
        logger.debug("API search: Awaiting request for query %s.", user_query)
        return await request.send_request(params=params)
