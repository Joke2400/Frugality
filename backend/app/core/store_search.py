"""Contains strategies for performing store searches."""
from typing import Coroutine
from httpx import Response

from backend.app.api import request
from backend.app.api import payload

from backend.app.core import parse
from backend.app.core import tasks
from backend.app.core import config
from backend.app.core.orm import schemas
from backend.app.core.orm import crud
from backend.app.core.search_context import (
    SearchContext,
    APISearchState,
    DBSearchState
)

from backend.app.utils import patterns
from backend.app.utils.util_funcs import assert_never
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

# Can be disabled in settings.cfg if needed for debugging.
PERFORM_API_SEARCHES = bool(
    config.parser["APP"]["perform_extern_api_searches"])
PERFORM_DB_SEARCHES = bool(
    config.parser["APP"]["perform_intern_db_searches"])


class DBStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> Coroutine[
                    None, None,
                    tuple[DBSearchState, list[schemas.StoreDB]]
                ]:
        """Perform a search on the database and return a result.

        Args:
            query (schemas.StoreQuery):
                A query of type schemas.StoreQuery is required.
            context (SearchContext):
                A search context is required to be provided.

        Raises:
            TypeError:
                Raised if kwarg 'context' was not provided or value was not
                an instance of SearchContext

        Returns:
            Coroutine[
                None, None,
                tuple[DBSearchState, list[schemas.StoreDB]]
            ]:
                Returns a Coroutine, the final value is a tuple containing
                a search state Enum, and the results retrieved as a list.
                List may be empty if no results were found.
        """
        if not PERFORM_DB_SEARCHES:
            logger.info("Search failed, DB searches disabled in config.")
            return DBSearchState.FAIL, []
        context: SearchContext | None = kwargs.get("context")
        query: schemas.StoreQuery | None = kwargs.get("query")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        if not isinstance(query, schemas.StoreQuery):
            raise TypeError("Required query type was not provided.")

        # Always using the ID if it's provided, even if the ID search fails,
        # but the name search would not (less complexity).
        if query.store_id is not None:
            result = crud.get_store_by_id(query.store_id)
        else:
            result = crud.get_stores_by_name(query.store_name)
        match result:
            case [] | None:
                logger.info("DB search: Failed to find items for query %s.",
                            query)
                return DBSearchState.FAIL, []
            case list() as data:
                logger.info("DB search: Got %s results for query %s.",
                            len(data), query)
                return DBSearchState.SUCCESS, data
            case schemas.StoreDB() as data:
                logger.info("DB search: Got result for query %s.", query)
                return DBSearchState.SUCCESS, [data]
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
            ) -> Coroutine[
                    None, None,
                    tuple[APISearchState, list[schemas.Store]]
                ]:
        """Perform a search on the external API and return a result.

        Args:
            query (schemas.StoreQuery):
                A query of type schemas.StoreQuery is required.
            context (SearchContext):
                A search context is required to be provided.

        Raises:
            TypeError:
                Raised if kwarg 'context' was not provided or value was not
                an instance of SearchContext

        Returns:
            Coroutine[
                None, None,
                tuple[APISearchState, list[schemas.Store]]
            ]:
                Returns a Coroutine, the final value is a tuple containing
                a search state Enum, and the results retrieved as a list.
                List may be empty if no results were found.
        """
        if not PERFORM_API_SEARCHES:
            logger.info("Search failed, API searches disabled in config.")
            return APISearchState.FAIL, []
        context: SearchContext | None = kwargs.get("context")
        query: schemas.StoreQuery | None = kwargs.get("query")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        if not isinstance(query, schemas.StoreQuery):
            raise TypeError("Required query type was not provided.")

        if (response := await cls._send_store_request(query=query)) is None:
            logger.error(
                "Received no API response to parse.")
            return APISearchState.NO_RESPONSE, []
        match parse.parse_store_response(response, query):
            case None:
                logger.error("Could not parse stores from API response.")
                return APISearchState.PARSE_ERROR, []
            case []:
                logger.info(
                    "API search: Failed to find stores for query %s.",
                    context.query)
                return APISearchState.FAIL, []
            case list() as data:
                logger.info("API search: Got %s results for query %s.",
                            len(data), context.query)
                # Add background task to save results to SearchContext
                context.tasks.add_task(
                    tasks.save_store_results, results=data)
                return APISearchState.SUCCESS, data
            case _ as data:
                assert_never(data)

    @classmethod
    async def _send_store_request(
            cls, query: schemas.StoreQuery
            ) -> Coroutine[None, None, Response | None]:
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
            store_query: str = str(query.store_name)
        params = payload.build_request_payload(
            method="post",
            operation=payload.Operation.STORE_SEARCH,
            variables=payload.build_store_variables(store_query),
            timeout=10)
        logger.debug("API search: Awaiting request for query %s.", query)
        return await request.send_request(params=params)
