from requests import post, Response
import asyncio
import json

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm
from api import s_queries
import core

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__)
query_logger = lgm.get_logger(name="query", level=20)


def send_post(query_string: str, params: dict) -> Response:
    response = post(url=api_url, json=params, timeout=1)
    logger.debug(
        f"Queried: '{query_string}', got response [{response.status_code}]")
    status = response.status_code
    response = json.loads(response.text)
    query_logger.debug(
        f"Queried: '{query_string}', got response" +
        f"[{status}]\nResponse text:" +
        json.dumps(response, indent=4))
    return response


async def async_send_post(query: str, variables: dict,
                          operation: str, query_item: core.QueryItem
                          ) -> tuple[Response, core.QueryItem]:
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation}
    query_string = variables["query"]
    response = await asyncio.to_thread(send_post, query_string, params)
    return response, query_item


async def api_fetch_products(store_id: str,
                             product_queries: list[core.QueryItem],
                             limit: int = 24
                             ) -> list[tuple[Response, core.QueryItem]]:
    operation = "GetProductByName"
    query = s_queries[operation]  # Get predefined GraphQL query
    tasks = []

    for count, p in enumerate(product_queries):
        variables = {
            "StoreID": store_id,
            "limit": limit,
            "query": p.name,
            "slugs": p.category,
        }
        logger.debug(
            f"Appending query @ index: {count} " +
            f"[Query: '{p.name}' Category: '{p.category}']")
        tasks.append(
            async_send_post(
                query=query,
                variables=variables,
                operation=operation,
                query_item=p))
    logger.debug(
        f"Async tasks len(): {len(tasks)}\n")
    return await asyncio.gather(*tasks)


def api_get_store():
    pass