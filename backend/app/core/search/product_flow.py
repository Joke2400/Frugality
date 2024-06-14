"""Contains strategies for performing product searches."""
import asyncio
from typing import Any, TypeAlias
from collections import defaultdict
from httpx import Response

from app.api import request
from app.api import payload

from app.core import parse, typedefs
from app.core.orm import schemas
from app.core.orm import operations
from app.core.search.state import SearchState

from app.utils import patterns
from app.utils.logging import LoggerManager

from app.utils.util_funcs import timer

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


QueryDictType: TypeAlias = dict[str, str | int | SearchState]


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
        query: schemas.ProductQuery | None = kwargs.get("query")
        if not isinstance(query, schemas.ProductQuery):
            raise TypeError(
                "A 'query' param of type ProductQuery must be provided.")
        results, to_forward, = cls._fetch_products(
            user_query=query, threshold=10)
        if len(to_forward) != 0:  # Temporary logic
            return SearchState.FAIL, results, to_forward
        return SearchState.SUCCESS, results, []

    @classmethod
    @timer
    def _fetch_products(
            cls, user_query: schemas.ProductQuery, threshold: int
            ) -> tuple[
                dict[int, list[typedefs.DBProductResultItem]],
                list[QueryDictType]]:
        results: dict[  # Gotta love all the typing gore here
            int, list[typedefs.DBProductResultItem]] = defaultdict(list)
        to_forward: list[QueryDictType] = []
        for store_id in user_query.stores:
            store_results = results[store_id]  # Get the store result list
            for query_dict in user_query.queries:
                combined_dict: QueryDictType = {
                    "store_id": store_id,
                    "state": SearchState.FAIL  # Set the default state to FAIL
                }
                combined_dict.update(query_dict)  # Add the rest of the data
                result: list[typedefs.ProductTupleDB] = operations.\
                    get_recent_complete_product_records(
                        query=query_dict["query"],
                        store_id=store_id,
                        timedelta_hours=24)
                logger.debug(
                    "DB Search: Found %s results for query: ('%s' %s)",
                    len(results), query_dict["query"], store_id)
                # Set the state variable based on threshold
                if len(result) >= threshold:
                    combined_dict["state"] = SearchState.SUCCESS
                else:
                    if 0 < len(result) < threshold:
                        combined_dict["state"] = SearchState.PARTIAL_RESULT
                    to_forward.append(combined_dict)
                store_results.append((combined_dict, result))
        return results, to_forward


class APIProductSearchStrategy(patterns.Strategy):

    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
            ) -> typedefs.APIProductSearchResult:
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
