"""Contains strategies for performing store searches."""
from typing import Coroutine

from backend.app.api import request
from backend.app.api import payload

from backend.app.core import parse
from backend.app.core import tasks
from backend.app.core.search_context import SearchContext
from backend.app.core.search_context import APISearchState, DBSearchState
from backend.app.core.orm import schemas
from backend.app.core.orm import crud

from backend.app.utils import patterns
from backend.app.utils.util_funcs import assert_never
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


class DBStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, method should
    be called via SearchContext.execute_strategy()
    """

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> Coroutine[
                    None, None,
                    tuple[DBSearchState, list[schemas.StoreDB]]
                ]:
        """Perform a search query on the database and return a result.

        TODO: Eliminate side-effects by passing a query in via kwargs.

        Args:
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
                Returns a Coroutine, final value is a tuple containing
                a search state Enum, and the results retrieved as a list.
                List may be empty if no results were found.
        """
        context: SearchContext | None = kwargs.get("context")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        query: schemas.StoreQuery = context.query

        # Always using the ID if it's provided, even if the ID search fails,
        # but the name search would not (less complexity).
        if query.store_id is not None:
            result = crud.get_store_by_id(query.store_id)
        else:
            result = crud.get_stores_by_name(query.store_name)
        match result:
            case [] | None:
                logger.info("DB search: Failed to find items for query %s.",
                            context.query)
                return DBSearchState.FAIL, []
            case list() as data:
                logger.info("DB search: Got %s results for query %s.",
                            len(data), context.query)
                return DBSearchState.SUCCESS, data
            case schemas.StoreDB() as data:
                logger.info("DB search: Got result for query %s.",
                            context.query)
                return DBSearchState.SUCCESS, [data]
            case _ as data:
                assert_never(data)


class APIStoreSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for a store from the API.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, method should
    be called via SearchContext.execute_strategy()
    """

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> Coroutine[
                    None, None,
                    tuple[APISearchState, list[schemas.Store]]
                ]:
        """Perform a search query on the external API and return a result.

        TODO: Eliminate side-effects by passing a query in via kwargs.
        TODO: Split function, too long & too hard to test.

        Args:
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
                Returns a Coroutine, final value is a tuple containing
                a search state Enum, and the results retrieved as a list.
                List may be empty if no results were found.
        """
        context: SearchContext | None = kwargs.get("context")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        query: schemas.StoreQuery = context.query
        if query.store_id is not None:
            query_value: str = str(query.store_id)
        else:
            query_value: str = str(query.store_name)
        params = payload.build_request_payload(
            method="post",
            operation=payload.Operation.STORE_SEARCH,
            variables=payload.build_store_variables(query_value),
            timeout=10)

        # Fetch API response
        logger.debug("API search: Awaiting request for query %s.",
                     context.query)
        if (response := await request.send_request(params=params)) is None:
            logger.error(
                "Received no API response to parse.")
            return APISearchState.NO_RESPONSE, []

        # TODO: Split the above code to another function, too hard to test this

        # Parse API response
        logger.debug("API search: Parsing response for query %s.",
                     context.query)
        match parse.parse_store_response(response, query_value):
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
                context.tasks.add_task(
                    tasks.save_store_results, results=data)
                return APISearchState.SUCCESS, data
            case _ as data:
                assert_never(data)
