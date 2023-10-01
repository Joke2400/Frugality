"""Contains functions for managing product query flow."""

import asyncio
from typing import Any

from api import api_fetch_products
from utils import get_quantity_from_string
from utils import LoggerManager

from .product_parser import ProductQueryParser
from .store import Store

logger = LoggerManager.get_logger(name=__name__)


def parse_user_query(data: dict) -> dict | None:
    """Take in a dict, parse and format query data from it.

    Args:
        data (dict): Dict containing 'name', 'count' and
        'category' keys (str, int, str).

    Returns:
        dict | None: If query can be parsed, returns dict
        fields. Otherwise it returns 'None'.
    """
    if not isinstance(data, dict):
        return None
    try:
        if (query := str(data["query"]).strip()) == "":
            return None
    except (ValueError, KeyError) as err:
        logger.debug(err)
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


async def get_products_from_api(
        queries: list[dict],
        stores: list[Store],
        limit: int = 24) -> list[list[tuple[dict, dict | None]]]:
    """Query one or more stores from the api with a list of queries.

    Args:
        queries (list[dict]): Queries to query.
        stores (list[Store]): Stores to query.
        limit (int, optional): API result length limit Defaults to 24.

    Returns:
        list[list[tuple[dict, dict | None]]]: List of lists each containing a
        tuple with the query item(dict) and its result(dict or None)
    """    
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
        stores: list[Store]) -> list[tuple[str, list[dict]]]:
    """Execute a store search and process the results into dictionaries.

    Args:
        queries (list[dict]): Queries to query.
        stores (list[Store]): Stores to query.

    Returns:
        list[tuple[str, list[dict]]]: List of tuples each containing the
        store slug and the results dictionary.
    """
    data = await get_products_from_api(queries=queries, stores=stores)

    parsers = []
    store_results = []
    for inx, item in enumerate(data, start=0):
        store = stores[inx]
        query_results = []
        for query, response in item:
            if response is not None:
                parser = ProductQueryParser(
                    response=response,
                    query=query,
                    store=query.pop("store"))
                query_results.append(parser.dictify())
                parsers.append(parser)
        store_results.append((str(store.slug), query_results))
    return store_results


def get_products_from_db(queries: list[dict]):
    pass


def add_product_query(request: dict, products: list[dict]
                      ) -> tuple[list[dict], int]:
    """Add a product query to the provided products list.

    added is set to True if a new query was appended to list.
    found is returned as True if product query was already in list,
    and it's count was thus incremented.
    """
    logger.debug("Adding a product query to products list...")
    key: Any = request.get("product", None)
    if not (product := parse_user_query(key)):
        return products, 400
    for i in products:
        if i["slug"] == product["slug"]:
            i["count"] += product["count"]
            logger.debug("Added '%s' to count of: '%s'.",
                         product["count"], i["query"])
            return products, 200
    if not len(products) >= 30:
        products.append(product)
        logger.debug("Added new query: '%s' to products list.",
                     product["query"])
        return products, 201
    return products, 404


def remove_product_query(request: dict, products: list[dict]
                         ) -> tuple[list[dict], int]:
    """Remove a product query from the provided products list."""
    logger.debug("Removing a product query from products list...")
    slug = request.get("slug", None)
    if not isinstance(slug, str):
        return products, 400

    results = list(filter(lambda i: i["slug"] == slug, products))
    if len(results) > 0:
        item = results[0]
        if item["count"] > 1:
            item["count"] -= 1
            logger.debug("Reduced count of %s, in product queries.", item)
        else:
            products.remove(item)
            logger.debug("Removed product %s, from product queries.", item)
        return products, 200
    return products, 404
