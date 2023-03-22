"""Contains functions for core app functionality."""

import json
from typing import Any

from utils import regex_search
from utils import regex_findall
from utils import LoggerManager
from api import api_fetch_products
from api import api_fetch_store
from .app_classes import ProductList


logger = LoggerManager.get_logger(name=__name__)


def get_quantity_from_string(string: str) -> tuple[int, str] | None:
    """Get a quantity from a given string.

    Returns a tuple containing the quantity as an integer.
    And the unit of the extracted quantity as a string.
    Units are ex: l, dl, cl, ml, kg, g, mg

    Args:
        string (str): String to be matched against.

    Returns:
        tuple[int, str] | None: Only returns a tuple if both
        matches are found and are valid. Otherwise returns None.
    """
    result = regex_search(r"(\d+)\s?(l|dl|cl|ml|kg|g|mg)", string)
    if result is not None:
        if result not in (None, ""):
            try:
                values = (int(result.group(1)), result.group(2))
                logger.debug(
                    "Retrieved values %s from string: %s", values, string)
                return values
            except ValueError:
                logger.exception("Could not convert to int: %s", result[0])
    logger.debug("Could not extract quantity from string: %s", string)
    return None


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


async def execute_store_product_search(
        queries: list[dict],
        store: tuple[str, str],
        limit: int = 24) -> dict[str, list[ProductList]]:
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
    logger.debug("Running product search for store '%s'.", store[0])
    data = await api_fetch_products(
        store_id=store[1],
        queries=queries,
        limit=limit)
    product_lists = []
    logger.debug("Creating ProductList(s) for %s items.", len(data))
    for response, query_item in data:
        if response is None:
            logger.error(
                "Cannot create ProductList, response was 'None'. Query: %s",
                query_item["query"])
        products = ProductList(
            response=json.loads(response.text),
            query_item=query_item,
            store=store)
        product_lists.append(products)
    return {store[0]: product_lists}


def parse_store_from_string(string: str) -> tuple[str | None, str | None]:
    """Find a store name and/or ID from a string using a RegEx pattern.

    Return results as a tuple.

    Args:
        string (str): String to parse.

    Returns:
        tuple[str | None, str | None]: Name and ID of store as strings.
    """
    logger.debug("Parsing store from string: '%s'", string)
    data = regex_findall(
        r"\d+|^(?:\s*\b)\b[A-Za-zåäö\s-]+(?=\s?)", string.strip())

    def is_digits(string: Any) -> str | None:
        try:
            i = str(int(string.strip()))
        except ValueError:
            return None
        return i

    s_name, s_id = None, None
    match data:

        case [str(), str()] as data:
            try:
                s_name = str(data[0]).strip()
            except ValueError as err:
                logger.exception(err)
            if i := is_digits(data[1]):
                s_id = i

        case [str()] as data:
            if i := is_digits(data[0]):
                s_id = i
            else:
                try:
                    s_name = str(data[0]).strip()
                except ValueError as err:
                    logger.exception(err)
        case _:
            pass

    logger.debug("Parsed store data from string -> ('%s', %s)", s_name, s_id)
    return (s_name, s_id)


def parse_and_validate_store(query_data: tuple[str | None, str | None],
                             response: dict) -> tuple[str, str] | None:
    """Parse store from API response.

    Args:
        query_data tuple[str | None, str | None]: Queried store name and ID.
        response (dict): Response body as python dict.

    Returns:
        tuple[str, str] | None: Store name and ID as a tuple
    """
    store = None
    try:
        store = response["data"]["store"]
    except KeyError:
        try:
            stores = response["data"]["searchStores"]["stores"]
        except KeyError as err:
            logger.exception(err)
            return None
        query_slug = "-".join(str(query_data[0]).lower().split())
        for i in stores:
            if "-".join(i["name"].lower().split()) == query_slug:
                logger.debug("Parsed store ('%s', '%s') from response",
                             i["name"], i["id"])
                return (i.get("name"), i.get("id"))
        logger.debug("Could not parse a store from response.")
        return None
    try:
        if store["id"].strip() == query_data[1]:
            logger.debug("Parsed store ('%s', '%s') from response",
                         store["name"], store["id"])
            return (store.get("name"), store.get("id"))
    except (KeyError, ValueError) as err:
        logger.exception(err)
        return None

    logger.debug("Could not parse a store from response.")
    return None


def execute_store_search(query_data: tuple[str | None, str | None]
                         ) -> tuple[str, str] | None:
    """Parse, execute and validate a store search using a given string.

    Returns:
        tuple[str, str] | None: Store name and ID, None if not found.
    """
    logger.debug("Fetching store from api: %s", query_data)
    response = api_fetch_store(query_data=query_data)
    if not response:
        return None
    logger.debug("Parsing response from api: %s", response)
    return parse_and_validate_store(query_data=query_data,
                                    response=response)
