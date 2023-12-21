import asyncio
from typing import Any

from app.core import parse, tasks
from app.core.search_context import SearchContext
from app.core.orm import schemas
from app.api import request
from app.api.skaupat import query as query_funcs
from app.utils import patterns
from app.utils.logging import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
ProductSearchResultT = \
    list[
        tuple[
            dict[str, str | int],
            list[
                tuple[
                    schemas.Product,
                    schemas.ProductData
                ]
            ]
        ]
    ]

# TODO: Might do good with some refactoring in this file


class DBProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(context: SearchContext) -> None:
        # TODO: This function
        pass


class APIProductSearchStrategy(patterns.Strategy):

    @staticmethod
    async def execute(
            context: SearchContext
            ) -> tuple[ProductSearchResultT, ProductSearchResultT]:
        async_tasks = []
        user_query: schemas.ProductQuery = context.query
        for store_id in user_query.stores:
            for query in user_query.queries:
                params = query_funcs.build_request_params(
                    method="post",
                    operation=query_funcs.Operation.PRODUCT_SEARCH,
                    variables=query_funcs.build_product_search_vars(
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
