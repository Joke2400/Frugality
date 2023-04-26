
import json
import asyncio

from utils import get_quantity_from_string
from utils import LoggerManager
from api import api_fetch_products
from .product_classes import ProductList

logger = LoggerManager.get_logger(name=__name__)


def parse_query_data(data: dict) -> dict | None:
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


async def execute_product_search(
        queries: list[dict],
        stores: list[tuple[str, str, str]],
        limit: int = 24):
    """Run product search for a given store.

    Args:
        queries (list[dict]): List of queries to query.
        store (tuple[str, str]): Store name and ID as a tuple.
        limit (int, optional): Limit for amount of products to retrieve.
        Defaults to 24.

    Returns:
        dict[str, list[ProductList]]: Returns a dict with a single key-value
        pair. Key is the name of the store queried. Value for the key is a
        list of ProductList(s).
    """
    tasks = []
    for store in stores:
        tasks.append(asyncio.create_task(
            api_fetch_products(
                store=store,
                queries=queries,
                limit=limit)))
    data = await asyncio.gather(*tasks)

    product_lists = []
    for index, item in enumerate(data, start=0):
        store = stores[index]
        products_list = []
        for query_item, response in item:
            products = ProductList(
                query_item=query_item,
                response=json.loads(response.text),
                store=store)
            products_list.append(products)
        product_lists.append({store[0]: products_list})
    return product_lists