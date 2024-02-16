"""Contains strategies for performing product searches."""
import asyncio
from typing import Any

from backend.app.api import request
from backend.app.api import payload

from backend.app.core import parse
from backend.app.core import tasks
from backend.app.core.search_context import SearchContext
from backend.app.core.orm import schemas
from backend.app.core.typedefs import ProductResultT

from backend.app.utils import patterns
from backend.app.utils.logging import LoggerManager


logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)


# TODO: Might do good with some refactoring in this file


class DBProductSearchStrategy(patterns.Strategy):
    """Strategy pattern implementation for searching for products from the DB.

    See patterns.Strategy for ABC implementation.

    Implements execute() abstractmethod, the method should
    be called via SearchContext.execute_strategy()
    """
    @staticmethod
    async def execute(*args, **kwargs) -> None:
        context: SearchContext | None = kwargs.get("context")
        query: schemas.ProductQuery = kwargs.get("query")
        if not isinstance(context, SearchContext):
            raise TypeError("Required search context was not provided.")
        if not isinstance(query, schemas.ProductQuery):
            pass


class APIProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[ProductResultT, ProductResultT]:
        async_tasks = []
        user_query: schemas.ProductQuery = context.query
        for store_id in user_query.stores:
            for query in user_query.queries:
                params = payload.build_request_payload(
                    method="post",
                    operation=payload.Operation.PRODUCT_SEARCH,
                    variables=payload.build_product_variables(
                        store_id=store_id, query=query),
                    timeout=10)
                logger.debug(
                    "Creating task for: (store_id: %s, query: %s)",
                    store_id, query)
                async_tasks.append(asyncio.create_task(
                    send_product_query(query=query, params=params)))
        results = await asyncio.gather(*async_tasks)
        successful_queries = []
        failed_queries = []
        for result in results:
            if len(result[1]) == 0:
                failed_queries.append(result)
            else:
                successful_queries.append(result)
        context.background_tasks.add_task(
            tasks.save_product_results, results=successful_queries)
        return successful_queries, failed_queries


async def send_product_query(
        query: dict[str, str], params: dict[str, Any]
        ) -> tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]:
    response = await request.send_request(params=params)
    return parse.parse_product_response(
        response=response,
        query=query
    )
