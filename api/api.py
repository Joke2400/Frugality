"""Contains functions for interfacing with api."""

import asyncio
import json

from httpx import Client, AsyncClient
from httpx import HTTPError, RequestError
from httpx import Response

from utils import LoggerManager
from data.urls import SKaupatURLs as S_urls
from .graphql_queries import queries as graphql_queries

logger = LoggerManager.get_logger(name=__name__)
query_logger = LoggerManager.get_logger(name="query", level=20)


def log_request(request):
    query_logger.debug(
        "Request event hook: %s %s - Waiting for response",
        request.method, request.url)


def log_response(response):
    request = response.request
    query_logger.debug(
        "Response event hook: %s %s - Status %s",
        request.method, request.url, response.status_code)


async def async_log_request(request):
    log_request(request)


async def async_log_response(response):
    log_response(response)


API_URL = S_urls.api_url
client = Client(
    event_hooks={'response': [log_response],
                 'request': [log_request]})

async_client = AsyncClient(
    event_hooks={'response': [async_log_response],
                 'request': [async_log_request]})


def post_request(url: str, params: dict,
                 timeout: int = 10) -> Response | None:
    """Send a post request with JSON body to a given URL.

    Args:
        url (str): URL to send request to.
        params (dict): JSON parameters.
        timeout (int, optional): Timeout in seconds Defaults to 10.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, return None.
    """
    try:
        response = client.post(url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except (HTTPError, RequestError) as err:
        logger.exception(err)
        return None
    content = json.loads(response.text)
    query_logger.debug("%s", json.dumps(
        content, indent=4))
    return response


async def async_post_request(url: str, params: dict,
                             timeout: int = 15) -> Response | None:
    """Asynchronously send a post request with JSON body to a given URL.

    Args:
        url (str): URL to send request to.
        params (dict): JSON parameters.
        timeout (int, optional): Timeout in seconds Defaults to 10.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, return None.
    """
    try:
        response = await async_client.post(
            url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except (HTTPError, RequestError) as err:
        logger.exception(err)
        return None
    content = json.loads(response.text)
    query_logger.debug("%s", json.dumps(
        content, indent=4))
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
        "operation_name": operation}
    response = post_request(url=API_URL, params=params)
    if not response:
        return None
    content = json.loads(response.text)
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
            "StoreID": str(int(query_data[1]))}
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
            "query": str(query_data[0])}
    except ValueError as err:
        logger.exception(err)
        return None
    operation = "StoreSearch"
    return (operation, variables)


async def async_product_search(query: dict, **kwargs):
    """Return query item with Response when calling async_post_request."""
    result = await async_post_request(**kwargs)
    return query, result


async def api_fetch_products(queries: list[dict],
                             store: tuple[str, str, str],
                             limit: int = 24):
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
    logger.debug("Creating tasks for store: '%s'", store[0])
    for inx, item in enumerate(queries):
        logger.debug(
            "Query: '%s' Category: '%s' @ list index: %s",
            item["query"], item["category"], inx)
        params = {
            "operation_name": operation,
            "query": query_string,
            "variables": {
                "StoreID": store[1],
                "limit": limit,
                "query": item["query"],
                "slugs": item["category"]}}
        tasks.append(asyncio.ensure_future(
            async_product_search(query=item, url=API_URL, params=params)))

    logger.debug("Length of tasks: %s", len(tasks))
    results = await asyncio.gather(*tasks)
    return {store[2]: results}
