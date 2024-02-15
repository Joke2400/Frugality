"""Contains strategies for performing store searches."""
from typing import Coroutine

from backend.app.api import request
from backend.app.api import request_funcs

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
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> Coroutine[
                    None, None,
                    tuple[DBSearchState, list[schemas.StoreDB]]
                ]:
        """TODO: DOCSTRING, function doesn't use async yet"""
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
    """TODO: DOCSTRING"""

    @staticmethod
    async def execute(
            *args, **kwargs
            ) -> Coroutine[
                    None, None,
                    tuple[APISearchState, list[schemas.Store]]
                ]:
        """TODO: DOCSTRING"""
        context: SearchContext | None = kwargs.get("context")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        query: schemas.StoreQuery = context.query
        if query.store_id is not None:
            query_value: str = str(query.store_id)
        else:
            query_value: str = str(query.store_name)
        params = request_funcs.build_request_parameters(
            method="post",
            operation=request_funcs.Operation.STORE_SEARCH,
            variables=request_funcs.build_store_variables(query_value),
            timeout=10)

        # Fetch API response
        logger.debug("API search: Awaiting request for query %s.",
                     context.query)
        if (response := await request.send_request(params=params)) is None:
            logger.error(
                "Received no API response to parse.")
            return APISearchState.NO_RESPONSE, []

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
