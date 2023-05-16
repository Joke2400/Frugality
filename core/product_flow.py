"""Contains functions for managing product query flow."""

import httpx
import asyncio

from api import api_fetch_products
from utils import get_quantity_from_string
from utils import LoggerManager

from .product_parser import ProductQueryParser
from .store import Store

logger = LoggerManager.get_logger(name=__name__)


def parse_user_query(data: dict) -> dict | None:
    """Take in a dict, parse and format query data from it.

    Args:
        data (dict): Dict containing 'query', 'count' and
        'category' keys (str, int, str).

    Returns:
        dict | None: If query can be parsed, returns dict
        fields. Otherwise it returns 'None'.
    """
    try:
        query = str(data["query"]).strip()
        if query == "":
            return None
    except (ValueError, KeyError) as err:
        logger.exception(err)
        return None
    quantity, unit = None, None
    if (result := get_quantity_from_string(query)) is not None:
        quantity, unit = result
    slug = "-".join(query.lower().split())
    try:
        count = abs(int(data["count"]))
        category = str(data["category"])
    except (ValueError, KeyError):
        if not isinstance(count, int):
            count = 1
        if not isinstance(category, str):
            category = ""
    return {
        "query": query,
        "count": count,
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "slug": slug
    }


def get_products_from_db(queries: list[dict]):
    pass


async def get_products_from_api(
        queries: list[dict],
        stores: list[Store],
        limit: int = 24) -> list[list[tuple[dict, dict | None]]]:
    tasks = []
    for store in stores:
        tasks.append(asyncio.create_task(
            api_fetch_products(
                queries=queries,
                store=store,
                limit=limit)))
    return await asyncio.gather(*tasks)


async def execute_product_search(
        queries: list[dict],
        stores: list[Store]) -> list[tuple[str, list[ProductQueryParser]]]:
    data = await get_products_from_api(queries=queries, stores=stores)

    store_results = []
    for inx, item in enumerate(data, start=0):
        store = stores[inx]
        query_results = []
        for query, response in item:
            if response is not None:
                parser = ProductQueryParser(
                    response=response,
                    query=query,
                    store=query["store"])
                query_results.append(parser)
        store_results.append((str(store.slug), query_results))
    return store_results
