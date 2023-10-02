"""Contains functions for interfacing with api."""


import json
import asyncio
import configparser

from core import Store
from utils import LoggerManager, FrugalityPaths

from .api_request import post_request, async_post_request
from .graphql_queries import queries as graphql_queries

logger = LoggerManager.get_logger(name=__name__)
config = configparser.ConfigParser()
config.read(FrugalityPaths.settings_path())

USER_AGENT = config["API"]["user_agent"]
API_ENDPOINT = config["SKAUPAT_URLS"]["graphql_endpoint"]
DO_LOGGING = bool("True" in config["API"]["do_query_logging"])


def get_store_by_id(data: tuple[None, str] | tuple[str, str]
                    ) -> tuple[str, dict] | None:
    """Return an operation name and variables dict for a search by ID.

    Use Store ID if available. If ID is not convertable to int,
    return get_store_by_name() instead.

    Args:
        data: (None, Store ID) or (Store name, Store ID)

    Returns:
        tuple[str, dict] | None: Operation Name and variables dict
        or None if ID or name not present in data.
    """
    try:
        variables = {
            "StoreID": str(int(data[1]))}
    except ValueError as err:
        if data[0] is None:
            logger.exception(err)
            return None
        return get_store_by_name(data)
    operation = "GetStoreInfo"
    return (operation, variables)


def get_store_by_name(data: tuple[str, None] | tuple[str, str]
                      ) -> tuple[str, dict] | None:
    """Return an operation name and variables dict for a search by name.

    If store name is not a string, return None.

    Args:
        data: (Store Name, None) or (Store name, Store ID)

    Returns:
        tuple[str, dict] | None: Operation name and variables dict.
    """
    try:
        variables = {
            "StoreBrand": None,
            "cursor": None,
            "query": str(data[0])}
    except ValueError as err:
        logger.exception(err)
        return None
    operation = "StoreSearch"
    return (operation, variables)


def fetch_store_from_api(store_query: tuple[str | None, str | None]
                         ) -> dict | None:
    """Fetch a store from the S-Kaupat api using either store name or id.

    Args:
        store_query: Store name and id as optional tuple values.

    Returns:
        A dictionary if request is successful, None if an exception
        occurred/no response received.
    """
    match store_query:
        case (None, str()) | (str(), str()) as store_query:
            if (data := get_store_by_id(store_query)) is None:
                return None
        case (str(), None) as store_query:
            if (data := get_store_by_name(store_query)) is None:
                return None
        case _:
            raise ValueError(
                f"api_store_query() was given an invalid value: {store_query}")

    params = {
        "timeout": 10,
        "headers": {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "User-Agent": USER_AGENT,
            "x-client-name": "skaupat-web"},
        "json": {
            "operation_name": data[0],
            "query": graphql_queries[data[0]],
            "variables": data[1]
        }
    }
    response = post_request(url=API_ENDPOINT, do_logging=DO_LOGGING,
                            params=params)
    if not response:
        logger.debug("API: No response to parse.")
        return None
    content = json.loads(response.text)
    return content


async def search_product(query: dict, params: dict) -> tuple[dict, dict | None]:
    """Return query item with Response when calling async_post_request."""
    logger.debug("[ASYNCIO] Awaiting post request: Query: '%s', %s",
                 query["query"], query["store"])
    response = await async_post_request(
        url=API_ENDPOINT,
        do_logging=DO_LOGGING,
        params=params)
    if not response:
        logger.debug("API: No response to parse.")
        return query, None
    content = json.loads(response.text)
    return query, content


async def api_fetch_products(
        queries: list[dict],
        store: Store,
        limit: int = 24) -> list[tuple[dict, dict | None]]:
    """Send api requests to fetch a bunch of product queries.

    Args:
        queries (list[dict]): Product queries as list of dictionaries.
        store (Store): Store to query.
        limit (int): Passed into query to limit result length.
        Defaults to 24.

    Returns:
        list[tuple[dict Response | None]]: Returns a future that gathers
        the results of the queries as a list of tuples containing
        queries and responses.
    """
    tasks = []
    logger.debug("Creating tasks for store: '%s', '%s'",
                 store.store_id, store.name)
    for index, query in enumerate(queries):
        params = {
            "timeout": 10,
            "headers": {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "User-Agent": USER_AGENT,
                "x-client-name": "skaupat-web"},
            "json": {
                "operation_name": "GetProductByName",
                "query": graphql_queries["GetProductByName"],
                "variables": {
                    "StoreID": store.store_id,
                    "limit": limit,
                    "query": query["query"],
                    "slugs": query["category"]
                }
            }
        }
        logger.debug(
            "Adding task: query='%s' category='%s' @ index=%s",
            query["query"], query["category"], index)
        query_dict = query.copy()
        query_dict["store"] = store
        tasks.append(
            asyncio.ensure_future(
                search_product(
                    query=query_dict,
                    params=params
                )
            )
        )
    logger.debug("[ASYNCIO] Calling asyncio.gather() - Tasks: %s", len(tasks))
    return await asyncio.gather(*tasks)
