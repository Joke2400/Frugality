import asyncio
import json
from httpx import Client, AsyncClient, Response, HTTPError, RequestError

from data.urls import SKaupatURLs as S_urls
from utils import LoggerManager
from .graphql_queries import queries as graphql_queries

logger = LoggerManager.get_logger(name=__name__)
query_logger = LoggerManager.get_logger(name="query", level=20)

client = Client()
async_client = AsyncClient()
API_URL = S_urls.api_url


def post_request(url: str, params: dict, timeout: int = 10,
                 log_str: str | None = None) -> Response | None:
    """Send a post request with JSON body to a given URL.

    Args:
        url (str): URL to send request to.
        params (dict): JSON parameters.
        timeout (int, optional): Timeout in seconds Defaults to 10.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, return None.
    """
    query_logger.debug("POST REQUEST; URL: %s; PARAMS: %s", url, params)
    try:
        response = client.post(url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except (HTTPError, RequestError) as err:
        logger.exception(err)
        return None
    if log_str is None:
        log_str = ""
    logger.debug("Status: %s | %s", response.status_code, log_str)
    return response


async def async_post_request(url: str, params: dict, timeout: int = 10,
                             log_str: str | None = None) -> Response | None:
    """Asynchronously send a post request with JSON body to a given URL.

    Args:
        url (str): URL to send request to.
        params (dict): JSON parameters.
        timeout (int, optional): Timeout in seconds Defaults to 10.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, return None.
    """
    query_logger.debug("POST REQUEST; URL: %s; PARAMS: %s", url, params)
    try:
        response = await async_client.post(
            url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except (HTTPError, RequestError) as err:
        logger.exception(err)
        return None
    if log_str is None:
        log_str = ""
    logger.debug("Status: %s | %s", response.status_code, log_str)
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
    query = graphql_queries[operation]
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation
    }
    log_str = f"Operation: '{operation}' Query: '{variables['query']}'"
    response = post_request(url=API_URL, params=params, log_str=log_str)
    if not response:
        return None
    content = json.loads(response.text)
    query_logger.debug("Response JSON: %s", json.dumps(content, indent=4))
    return content


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
            logger.exception(err)
            return None
        return get_store_by_name(query_data)
    operation = "GetStoreInfo"
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
        logger.exception(err)
        return None
    operation = "StoreSearch"
    return (operation, variables)


async def async_product_search(item: dict, **kwargs):
    """Return query item with Response when calling async_post_request."""
    result = await async_post_request(**kwargs)
    return result, item


async def api_fetch_products(queries: list[dict],
                             store_id: str,
                             limit: int = 24
                             ) -> list[tuple[Response, dict]]:
    """Asynchronously send api requests to fetch a list of product queries.

    Args:
        queries (list[dict]): Product queries as list of dictionaries.
        store_id (list[(str, str)]): Stores to query.
        limit (int, optional): Passed into query to limit result length.
        Defaults to 24.

    Returns:
        list[tuple[Response, dict]]: Returns a future that gathers
        the results of the queries as a list of responses and query dicts.
    """
    tasks = []
    operation = "GetProductByName"
    query_string = graphql_queries[operation]
    logger.debug("Creating tasks for StoreID: '%s'", store_id)
    for inx, item in enumerate(queries):
        logger.debug(
            "Query: '%s' Category: '%s' @ list index: %s",
            item["query"], item["category"], inx)
        params = {
            "operation_name": operation,
            "query": query_string,
            "variables": {
                "StoreID": store_id,
                "limit": limit,
                "query": item["query"],
                "slugs": item["category"]
            }
        }
        log_str = f"Operation: '{operation}' Product query: '{item['query']}'"
        tasks.append(asyncio.ensure_future(
            async_product_search(item, url=API_URL, params=params,
                                 log_str=log_str)))

    logger.debug("Length of tasks: %s", len(tasks))
    return await asyncio.gather(*tasks)
