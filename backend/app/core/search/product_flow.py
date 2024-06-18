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

from app.utils import patterns
from app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


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
        user_query: list[typedefs.ProductQueryDictT] = kwargs["user_query"]
        threshold: int = int(kwargs["threshold"])
        logger.debug("DB product search: Set threshold to %s", threshold)
        has_successful, has_partial = False, False
        queries_to_forward: list[typedefs.ProductQueryDictT] = []
        search_results: \
            dict[int, list[typedefs.DBProductResultItem]] = defaultdict(list)
        for query_dict in user_query:
            query_dict, results = cls._fetch_product_query(
                query_dict=query_dict,
                timedelta_hours=24,
                length_threshold=5)
            if query_dict["state"] is SearchState.SUCCESS:
                has_successful = True
            else:
                if query_dict["state"] is SearchState.PARTIAL_RESULT:
                    has_partial = True
                queries_to_forward.append(query_dict)
            search_results[int(query_dict["store_id"])].append(
                (query_dict, results))
        # Determine what the 'higher-level' SearchState needs to be set to
        if has_successful and len(queries_to_forward) == 0:
            logger.debug(
                "DB product search: Success!")
            return SearchState.SUCCESS, (search_results, [])
        if not has_partial and not has_successful:
            logger.debug(
                "DB product search: Failed to fulfill ANY user queries.")
            return SearchState.FAIL, (search_results, queries_to_forward)
        logger.debug(
            "DB product search: Was able to partially fulfill user queries")
        return SearchState.PARTIAL_RESULT, (search_results, queries_to_forward)

    @classmethod
    def _fetch_product_query(
            cls, query_dict: typedefs.ProductQueryDictT,
            timedelta_hours: int, length_threshold: int
            ) -> tuple[typedefs.ProductQueryDictT,
                       list[typedefs.ProductTupleDB]]:
        logger.debug(
            "DB search: Fetching results for query: %s", query_dict)
        results: list[typedefs.ProductTupleDB] = operations.\
            get_recent_complete_product_records(
                query=str(query_dict["query"]),
                store_id=int(query_dict["store_id"]),
                timedelta_hours=timedelta_hours)
        logger.debug(
            "DB Search: Found %s results for query: %s",
            len(results), query_dict)
        if len(results) >= length_threshold:
            query_dict["state"] = SearchState.SUCCESS
        elif 0 < len(results) < length_threshold:
            query_dict["state"] = SearchState.PARTIAL_RESULT
        return query_dict, results


class APIProductSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for products from the API.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """
    @classmethod
    async def execute(
            cls, *args: Any, **kwargs: Any
            ) -> typedefs.APIProductSearchResult:
        user_query: list[typedefs.ProductQueryDictT] = kwargs["user_query"]
        results_dict: \
            dict[int, list[typedefs.APIProductResultItem]] = defaultdict(list)
        tasks: list[asyncio.Task[
            tuple[typedefs.ProductQueryDictT,
                  list[typedefs.ProductTupleAPI]]]] = []
        for query_dict in user_query:
            logger.debug(
                "Creating task for query: %s", query_dict)
            task = asyncio.create_task(
                cls._fetch_product_query(query_dict=query_dict))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        has_successful = False
        for item in results:
            results_dict[int(item[0]["store_id"])].append(item)
            if item[0]["state"] is SearchState.SUCCESS:
                has_successful = True
        if not has_successful:
            return SearchState.FAIL, results_dict
        return SearchState.SUCCESS, results_dict


    @classmethod
    async def _fetch_product_query(
            cls, query_dict: typedefs.ProductQueryDictT
            ) -> tuple[typedefs.ProductQueryDictT,
                       list[typedefs.ProductTupleAPI]]:
        params = payload.build_request_payload(
            method="post",
            operation=payload.Operation.PRODUCT_SEARCH,
            variables=payload.build_product_variables(
                store_id=int(query_dict["store_id"]),
                query=str(query_dict["query"]),
                category=str(query_dict["category"])),
            timeout=10)
        logger.debug(
            "DB search: Fetching results for query: %s", query_dict)
        response = await request.send_request(params=params)
        query_dict, results = parse.parse_product_response(
                    response=response, query_dict=query_dict)
        logger.debug(
            "DB Search: Found %s results for query: %s",
            len(results), query_dict)
        return query_dict, results
