from requests import post, Response
import asyncio
import json

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm, timer
from api import s_queries
import core

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__)
query_logger = lgm.get_logger(name="query", level=20)


def send_post(query_string: str | None, params: dict) -> Response:
    response = post(url=api_url, json=params, timeout=10)
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
                          operation: str, query_item: core.Item
                          ) -> tuple[Response, core.Item]:
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation}
    query_string = variables["query"]
    response = await asyncio.to_thread(send_post, query_string, params)
    return response, query_item


async def api_fetch_products(store_id: str,
                             product_queries: list[core.Item],
                             limit: int = 24
                             ) -> list[tuple[Response, core.Item]]:
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


def api_get_store(store_name: str | None = None,
                  store_id: str | None = None) -> Response:
    if store_id is not None:
        operation = "GetStoreInfo"
        variables = {
            "StoreID": store_id
        }
    else:
        operation = "StoreSearch"
        variables = {
            "StoreBrand": None,
            "cursor": None,
            "query": str(store_name)
        }
    query = s_queries[operation]
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation
    }
    response = send_post(store_name, params)
    return response
