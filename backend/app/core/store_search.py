"""Contains strategies for performing store searches."""
from httpx import Response

from backend.app.api import request
from backend.app.api import payload

from backend.app.core import parse
from backend.app.core import config
from backend.app.core.orm import schemas
from backend.app.core.orm import crud
from backend.app.core.search_state import SearchState

from backend.app.utils import patterns
from backend.app.utils.util_funcs import assert_never
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

# Can be disabled in settings.cfg if needed for debugging.
PERFORM_DB_SEARCHES = (
    config.parser["APP"]["perform_db_searches"] in ("True", "true"))
PERFORM_API_SEARCHES = (
    config.parser["APP"]["perform_api_searches"] in ("True", "true"))


class DBStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> tuple[SearchState, list[schemas.StoreDB]]:
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
        if not PERFORM_DB_SEARCHES:
            logger.info("Store DB search failed, disabled in config.")
            return SearchState.FAIL, []
        query: schemas.StoreQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.StoreQuery):
            raise TypeError(
                "A 'query' param of type StoreQuery must be provided.")
        result: list[schemas.StoreDB] | schemas.StoreDB | None
        if query.store_id is not None:
            result = crud.get_store_by_id(query.store_id)
        else:
            result = crud.get_stores_by_name(query.store_name)  # type: ignore
        match result:
            case [] | None:
                logger.info("DB search: Failed to find stores for query: %s.",
                            query)
                return SearchState.FAIL, []
            case list() as data:
                logger.info(
                    "DB search: Got %s store results for query: %s.",
                    len(data), query)
                return SearchState.SUCCESS, data
            case schemas.StoreDB() as data:
                logger.info(
                    "DB search: Got 1 store results for query: %s.",
                    query)
                return SearchState.SUCCESS, [data]
            case _ as data:
                assert_never(data)


class APIStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the API.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """

    @classmethod
    async def execute(
            cls, *args, **kwargs
            ) -> tuple[SearchState, list[schemas.Store]]:
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
        if not PERFORM_API_SEARCHES:
            logger.info("Store API search failed, disabled in config.")
            return SearchState.FAIL, []
        query: schemas.StoreQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.StoreQuery):
            raise TypeError(
                "A 'query' param of type ProductQuery must be provided.")
        if (response := await cls._send_store_query(query=query)) is None:
            logger.error(
                "API search: Received no API response to parse.")
            return SearchState.NO_RESPONSE, []
        parsed = parse.parse_store_response(response, query)
        match parsed:
            case None:
                logger.error(
                    "API search: Failed to parse stores from API response.")
                return SearchState.PARSE_ERROR, []
            case []:
                logger.info(
                    "API search: Failed to find stores for query: %s.",
                    query)
                return SearchState.FAIL, []
            case list() as data:
                logger.info("API search: Got %s results for query: %s.",
                            len(data), query)
                return SearchState.SUCCESS, data
            case _ as data:
                assert_never(data)

    @staticmethod
    async def _send_store_query(
            query: schemas.StoreQuery
            ) -> Response | None:
        """Build API request payload and send store request.

        Args:
            query (schemas.StoreQuery):
                The store query to build the request with.

        Returns:
            Coroutine[
                None, None,
                Response | None
                ]:
                Coroutine which final value is either a httpx.Response
                or None if no response was received / an error occurred.
        """
        if query.store_id is not None:
            store_query: str = str(query.store_id)
        else:
            store_query = str(query.store_name)
        params = payload.build_request_payload(
            method="post",
            operation=payload.Operation.STORE_SEARCH,
            variables=payload.build_store_variables(store_query),
            timeout=10)
        logger.debug("API search: Awaiting request for query %s.", query)
        return await request.send_request(params=params)
