from requests import Response, exceptions, Session
import asyncio
import json

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm, timer
from api import s_queries
import core

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__)
query_logger = lgm.get_logger(name="query", level=20)

session = Session()


def post_request(url: str, params: dict, timeout: int = 10
                 ) -> Response | None:
    """Send a post request with JSON body to a given URL.

    Args:
        url (str): URL to send request to.
        params (dict): JSON parameters.
        timeout (int, optional): Timeout in seconds Defaults to 10.

    Returns:
        Response | None: Default returns a requests.response object.
        If an exception is raised, return None.
    """
    query_logger.debug("POST REQUEST; URL: %s; PARAMS: %s", url, params)
    try:
        response = session.post(url=url, json=params, timeout=timeout)
        response.raise_for_status()
    except exceptions.RequestException as err:
        logger.exception(err)
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
            logger.exception(err)
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
        logger.exception(err)
        return None
    operation = "StoreSearch"
    logger.debug("Request: %s, %s", operation, variables)
    return (operation, variables)


async def async_post_request(operation_name: str, variables: dict,
                             query: str, item: core.QueryItem
                             ) -> tuple[Response, core.QueryItem]:
    """Run post_request() in a separate thread using to_thread().

    Takes in params for the post request function.

    Args:
        operation_name (str): Name of the operation to be passed on.
        variables (dict): Query variables to passed on.
        query (str): Query string to be passed on.
        item (core.QueryItem): QueryItem to be returned with response.

    Returns:
        tuple[Response, core.QueryItem]: Returns a coroutine object and
        the corresponding QueryItem that was passed into the func.
    """
    params = {
        "operation_name": operation_name,
        "variables": variables,
        "query": query}
    response = await asyncio.to_thread(post_request,
                                       url=api_url, params=params)
    return response, item


async def api_fetch_products(queries: list[core.QueryItem],
                             store_id: str, limit: int = 24
                             ) -> list[tuple[Response, core.QueryItem]]:
    """Asynchronously send api requests to fetch a list of product queries.

    Args:
        queries (list[core.QueryItem]): Product queries as QueryItem instances.
        store_id (str): ID of store to query.
        limit (int, optional): Passed into query to limit result length.
        Defaults to 24.

    Returns:
        list[tuple[Response, core.QueryItem]]: Returns a future that gathers
        the results of the queries as a list of responses and query items.
    """
    tasks = []
    operation = "GetProductByName"
    query = s_queries[operation]
    for inx, item in enumerate(queries):
        logger.debug(
            "Query: '%s' Category: '%s' @ list index: %s",
            item.name, item.category, inx)
        variables = {
            "StoreID": store_id,
            "limit": limit,
            "query": item.name,
            "slugs": item.category,
        }
        tasks.append(
            async_post_request(
                operation_name=operation,
                variables=variables,
                query=query,
                item=item))
    logger.debug("Final length of tasks: %s", len(tasks))
    return await asyncio.gather(*tasks)
