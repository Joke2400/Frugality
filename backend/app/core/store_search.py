from typing import Callable

from backend.app.api import request
from backend.app.api.skaupat import query_utils

from backend.app.core import parse
from backend.app.core import tasks
from backend.app.core.search_context import SearchContext
from backend.app.core.search_context import SearchState
from backend.app.core.orm import schemas
from backend.app.core.orm import crud

from backend.app.utils import patterns
from backend.app.utils import exceptions
from backend.app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

# TODO: Might do good with some refactoring in this file


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
            crud_func = crud.get_stores_by_name
        # This is too hard to read, rework this function
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
        params = query_utils.build_request_params(
            method="post",
            operation=query_utils.Operation.STORE_SEARCH,
            variables=query_utils.build_store_search_vars(
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
                    tasks.save_store_results, results=data)
                return context.status, data
            case _ as data:
                raise exceptions.InvalidMatchCaseError(
                    f"Could not match value: {data} to a predefined case.")
