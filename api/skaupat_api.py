from requests import Response, exceptions, Session, post
import asyncio
import json

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm, timer
from api import s_queries
import core

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__)
query_logger = lgm.get_logger(name="query", level=20)


def post_request(url: str, params: dict, timeout: int = 10
                 ) -> Response | None:
    query_logger.debug("POST REQUEST; URL: %s; PARAMS: %s", url, params)
    try:
        response = post(url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except exceptions.RequestException as err:
        logger.debug(err)
        return None
    logger.debug("Status code: %s", response.status_code)
    return response


def api_fetch_store(query_data: tuple[str | None, str | None]
                    ) -> dict | None:
    """Use store name or ID to fetch store from API.

    Args:
        query_data tuple[str | None, str | None]:
        Store name and/or store ID.

    Raises:
        ValueError: Raised if query_data does not conform to the specified
        stuctural patterns.

    Returns:
        dict | None: Return response json as a python dict.
    """
    match query_data:
        case (None, str()) | (str(), str()) as query_data:
            if (data := get_store_by_id(query_data)) is None:
                return None
        case (str(), None) as query_data:
            if (data := get_store_by_name(query_data)) is None:
                return None
        case _:
            raise ValueError(
                f"api_store_query() was given an invalid value: {query_data}")

    operation, variables = data
    query = s_queries[operation]
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation
    }
    response = post_request(url=api_url, params=params)
    if not response:
        return None
    return json.loads(response.text)


def get_store_by_id(query_data: tuple[None, str] | tuple[str, str]
                    ) -> tuple[str, dict] | None:
    """Return an operation name and variables dict for a search by ID.

    Use Store ID if available. If ID is not convertable to int,
    return get_store_by_name() instead.

    Args:
        query_data tuple: (None, Store ID) or (Store name, Store ID)

    Returns:
        tuple[str, dict] | None: Operation Name and variables dict
        or None if ID or name not present in query_data.
    """
    try:
        variables = {
            "StoreID": str(int(query_data[1]))
        }
    except ValueError as err:
        if query_data[0] is None:
            logger.debug(err)
            return None
        return get_store_by_name(query_data)
    operation = "GetStoreInfo"
    logger.debug("Request: %s, %s", operation, variables)
    return (operation, variables)


def get_store_by_name(query_data: tuple[str, None] | tuple[str, str]
                      ) -> tuple[str, dict] | None:
    """Return an operation name and variables dict for a search by name.

    If store name is not a string, return None.

    Args:
        query_data tuple: (Store Name, None) or (Store name, Store ID)

    Returns:
        tuple[str, dict] | None: Operation name and variables dict.
    """
    try:
        variables = {
            "StoreBrand": None,
            "cursor": None,
            "query": str(query_data[0])
        }
    except ValueError as err:
        logger.debug(err)
        return None
    operation = "StoreSearch"
    logger.debug("Request: %s, %s", operation, variables)
    return (operation, variables)


async def async_send_post(query: str, variables: dict,
                          operation: str, query_item: core.Item
                          ) -> tuple[Response, core.Item]:
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation}
    query_string = variables["query"]
    response = await asyncio.to_thread(send_post, params, query_string)
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

