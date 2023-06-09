"""Contains functions for interfacing with api."""

import asyncio
import json

from httpx import Client, AsyncClient
from httpx import HTTPError, RequestError, ConnectError, ConnectTimeout
from httpx import Response, Request

from core import Store
from utils import LoggerManager
from data.urls import SKaupatURLs as S_urls
from .graphql_queries import queries as graphql_queries

logger = LoggerManager.get_logger(name=__name__)
query_logger = LoggerManager.get_logger(name="query", level=20)


def log_request(request: Request) -> None:
    """Log a request."""
    query_logger.debug(
        "Request event hook: %s %s - Waiting for response",
        request.method, request.url)


def log_response(response: Response) -> None:
    """Log a response."""
    request = response.request
    query_logger.debug(
        "Response event hook: %s %s - Status %s",
        request.method, request.url, response.status_code)


async def async_log_request(request: Request) -> None:
    """Log a request."""
    log_request(request)


async def async_log_response(response: Response) -> None:
    """Log a response."""
    log_response(response)


API_URL = S_urls.api_url
client = Client(
    event_hooks={'response': [log_response],
                 'request': [log_request]})

async_client = AsyncClient(
    event_hooks={'response': [async_log_response],
                 'request': [async_log_request]})


def post_request(url: str, params: dict, timeout: int = 10) -> Response | None:
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
        response = client.post(
            url=url, json=params, timeout=timeout)
        response.raise_for_status()

    except ConnectTimeout as err:
        query_logger.error(err)
        query_logger.info(
            "Connection timed out: %s %s",
            err.request.method, err.request.url)

    except ConnectError as err:
        query_logger.error(err)
        query_logger.info(
            "Could not establish connection to: %s %s",
            err.request.method, err.request.url)

    except (HTTPError, RequestError) as err:
        query_logger.exception(err)
    else:
        return response
    return None


async def async_post_request(url: str, params: dict, timeout: int = 10,
                             ) -> Response | None:
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

    except ConnectTimeout as err:
        query_logger.error(err)
        query_logger.info(
            "Connection timed out: %s %s",
            err.request.method, err.request.url)

    except ConnectError as err:
        query_logger.error(err)
        query_logger.info(
            "Could not establish connection to: %s %s",
            err.request.method, err.request.url)

    except (HTTPError, RequestError) as err:
        query_logger.exception(err)
    else:
        return response
    return None


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


async def async_product_search(query: dict, log_response_body: bool = False,
                               **kwargs) -> tuple[dict, dict | None]:
    """Return query item with Response when calling async_post_request."""
    logger.debug("[ASYNCIO] Awaiting post request: Query: '%s', %s",
                 query["query"], query["store"])
    response = await async_post_request(**kwargs)
    if response is not None:
        content = json.loads(response.text)
        slug = "-".join(content["data"]["store"]["name"].lower().split())
        if slug == query["store"].slug:
            logger.debug("Response store: '%s' == Query store: '%s'.",
                         slug, query["store"].slug)
        if log_response_body:
            query_logger.debug("%s", json.dumps(
                content, indent=4))
        return query, content
    query_logger.debug("Returning response as 'None'.")
    return query, None


async def api_fetch_products(
        queries: list[dict],
        store: Store,
        limit: int = 24) -> list[tuple[dict, dict | None]]:
    """Asynchronously send api requests to fetch a bunch of queries.

    Args:
        queries (list[dict]): Product queries as list of dictionaries.
        store (list[Store]): List of stores to query.
        limit (int): Passed into query to limit result length.
        Defaults to 24.

    Returns:
        list[tuple[dict Response | None]]: Returns a future that gathers
        the results of the queries as a list of tuples containing
        queries and responses.
    """
    tasks = []
    operation = "GetProductByName"
    graphql_query = graphql_queries[operation]
    logger.debug("Creating tasks for store: '%s', '%s'", store.store_id,
                 store.name)
    for inx, query in enumerate(queries):
        logger.debug(
            "Adding task: query='%s' category='%s' @ inx=%s",
            query["query"], query["category"], inx)
        params = {
            "operation_name": operation,
            "query": graphql_query,
            "variables": {
                "StoreID": store.store_id,
                "limit": limit,
                "query": query["query"],
                "slugs": query["category"]}}
        query_dict = query.copy()
        query_dict["store"] = store
        tasks.append(asyncio.ensure_future(
            async_product_search(query=query_dict, log_response_body=False,
                                 url=API_URL, params=params, timeout=20)))

    logger.debug("[ASYNCIO] Calling asyncio.gather() - Tasks: %s", len(tasks))
    return await asyncio.gather(*tasks)
