
import json
import asyncio

from utils import get_quantity_from_string
from utils import LoggerManager
from api import api_fetch_products
from .product_classes import ProductList
from .store import Store

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


def get_products_from_db(queries: list[dict]):
    pass


async def get_products_from_api(queries: list[dict],
                                stores: list[tuple[str, str, str]],
                                limit: int = 24):
    tasks = []
    for store in stores:
        tasks.append(asyncio.create_task(
            api_fetch_products(
                queries=queries,
                store_id=store[1],
                limit=limit)))
    return await asyncio.gather(*tasks)


def execute_product_search(queries: list[dict],
                           stores: list[tuple[str, str, str]]):
    # Get products from db
    
    



async def execute_product_search(
        queries: list[dict],
        stores: list[tuple[str, str, str]],
        limit: int = 24):
    print(queries)
    product_lists = []
    for index, item in enumerate(data, start=0):
        store = stores[index]
        products_list = []
        for query_item, response in item:
            products = ProductList(
                query_item=query_item,
                response=json.loads(response.text),
                store=store)
            print(products.products)
            products_list.append(products)
        product_lists.append({store[0]: products_list})
    return product_lists