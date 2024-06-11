"""Contains strategies for performing product searches."""
import asyncio
from typing import Any
from collections import defaultdict
from httpx import Response

from app.api import request
from app.api import payload

from app.core import parse, typedefs
from app.core.orm import schemas
from app.core.orm import operations
from app.core.search.state import SearchState

from app.utils import config, patterns
from app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)

# Can be disabled in settings.cfg if needed for debugging.
PERFORM_DB_SEARCHES = (
    config.parser["app"]["perform_db_searches"] in ("True", "true"))
PERFORM_API_SEARCHES = (
    config.parser["app"]["perform_api_searches"] in ("True", "true"))


class DBProductSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for products from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """
    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
                ) -> typedefs.DBProductSearchResult:
        if not PERFORM_DB_SEARCHES:
            logger.info("Product API search failed, disabled in config.")
            return SearchState.FAIL, {}
        query: schemas.ProductQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.ProductQuery):
            raise TypeError(
                "A 'query' param of type ProductQuery must be provided.")
        query_results = cls.get_products(user_query=query)
        results: dict[
            int, list[typedefs.DBProductResultItem]] = defaultdict(list)
        # TODO: this code below is spaghetti & needs refactoring
        all_failed = True
        for items, original_query in query_results:
            if len(items) == 0:
                # TODO: Is supposed to skip & forward to API
                # eq. SearchState.FAIL
                continue
            if len(items) < 5:
                # TODO: Threshold not reached, keep items but forward request
                # eq. SearchState.PARTIAL_RESULT
                pass
            all_failed = False
            results[int(original_query["store_id"])].append((original_query, items))
        if all_failed:
            return SearchState.FAIL, results
        return SearchState.SUCCESS, results


    @classmethod
    def get_products(
            cls, user_query: schemas.ProductQuery
            ) -> list[
                tuple[list[typedefs.DBProductItem], dict[str, str | int]]]:
        # Ideally, would fetch the records for multiple stores at once, but simpler
        # to organize the output like this, so doing it like this for now
        results: list[
            tuple[list[typedefs.DBProductItem], dict[str, str | int]]] = []
        for store_id in user_query.stores:  # TODO: < --Remove this row & query all specified store ids
            for query in user_query.queries:
                combined: dict[str, str | int] = {"store_id": store_id}
                combined.update(query)
                result: list[typedefs.DBProductItem] = operations.\
                    get_recent_complete_product_records(
                        query=query["query"],
                        store_ids=[store_id],
                        timedelta_hours=24)
                results.append((result, combined))
        return results


class APIProductSearchStrategy(patterns.Strategy):

    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
            ) -> typedefs.APIProductSearchResult:
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
        results: dict[
            int, list[typedefs.APIProductResultItem]] = defaultdict(list)
        # TODO: this code below is spaghetti & needs refactoring
        all_failed = True
        for response, original_query in responses:
            if response is None:
                # Add empty result to results
                original_query["state"] = SearchState.NO_RESPONSE
                results[int(original_query["store_id"])].append(
                    (original_query, []))
                continue
            # Add parsed result to results
            parsed = parse.parse_product_response(
                    response=response, query=original_query)
            if parsed[0]["state"] is SearchState.SUCCESS and all_failed:
                all_failed = False
            results[int(original_query["store_id"])].append(parsed)
        if all_failed:
            return SearchState.FAIL, results
        return SearchState.SUCCESS, results

    @classmethod
    async def _send_product_queries(
            cls, user_query: schemas.ProductQuery
            ) -> list[tuple[Response | None, dict[str, str | int]]]:

        # The task used for asyncio.gather()
        async def send_query(
                params: dict[str, Any], orig_query: dict[str, str | int]
                ) -> tuple[Response | None, dict[str, str | int]]:
            return await request.send_request(params=params), orig_query

        # TODO: Below code needs improvement
        tasks: list = []
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
