"""Contains strategies for performing product searches."""
import asyncio
from typing import Any
from collections import defaultdict
from httpx import Response

from backend.app.api import request
from backend.app.api import payload

from backend.app.core import parse
from backend.app.core import config
from backend.app.core.typedefs import ProductResultT
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


class DBProductSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for products from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """
    @staticmethod
    async def execute(*args, **kwargs) -> Any:
        query: schemas.ProductQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.ProductQuery):
            pass
        return SearchState.FAIL, {}


class APIProductSearchStrategy(patterns.Strategy):

    @classmethod
    async def execute(
            cls, *args, **kwargs
            ) -> ProductResultT:
        if not PERFORM_API_SEARCHES:
            logger.info("Product API search failed, disabled in config.")
            return SearchState.FAIL, {}
        query: schemas.ProductQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.ProductQuery):
            raise TypeError(
                "A 'query' param of type ProductQuery must be provided.")
        if not any((responses := await cls._send_product_queries(query))):
            logger.error(
                "API search: Received no API responses to parse.")
            return SearchState.NO_RESPONSE, {}
        results: dict[int, list] = defaultdict(list)
        for response, orig_query in responses:
            if response is None:
                # Add empty query to results
                results[int(orig_query["store_id"])].append(
                    (SearchState.NO_RESPONSE, orig_query, []))
                continue
            # Add parsed query to results
            results[int(orig_query["store_id"])].append(
                parse.parse_product_response(
                    response=response, query=orig_query))
        return SearchState.SUCCESS, results

    @classmethod
    async def _send_product_queries(
            cls, user_query: schemas.ProductQuery
            ) -> list[tuple[Response | None, dict[str, str | int]]]:

        async def send_query(
                params: dict[str, Any], orig_query: dict[str, str | int]
                ) -> tuple[Response | None, dict[str, str | int]]:
            return await request.send_request(params=params), orig_query

        tasks = []
        for store_id in user_query.stores:
            for query in user_query.queries:
                combined: dict[str, str | int] = {"store_id": store_id}
                combined.update(query)
                params = payload.build_request_payload(
                    method="post",
                    operation=payload.Operation.PRODUCT_SEARCH,
                    variables=payload.build_product_variables(
                        store_id=store_id, query=query),
                    timeout=10)
                logger.debug(
                    "Creating task for: (store_id: %s, query: %s)",
                    store_id, user_query)
                tasks.append(asyncio.create_task(
                    send_query(params, combined)))
        return await asyncio.gather(*tasks)
