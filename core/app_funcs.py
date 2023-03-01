from utils import timer, LoggerManager as lgm
from core import Item, ProductList
from api import api_fetch_products, api_fetch_store
from requests import Response
from typing import Any

import asyncio
import re

logger = lgm.get_logger(name=__name__)


def regex_search(pattern: str, string: str
                 ) -> re.Match[str] | None:
    """Scan through a string and return a single RegEx match.

    Returns a Match object if a match is found,
    returns None in other cases.

    Args:
        pattern (str): RegEx pattern as a raw string.
        string (str): String to be matched against

    Returns:
        re.Match[str] | None: Returns either a Match object or None
    """
    result = re.search(
        pattern=pattern,
        string=string,
        flags=re.I | re.M)
    logger.debug(
        "regex_search(): %s original: '%s'", result, string)
    return result


def regex_findall(pattern: str, string: str
                  ) -> list | None:
    """Scan through a string and return multiple RegEx matches.

    Args:
        pattern (str): RegEx pattern as a raw string.
        string (str): String to be matched against

    Returns:
        list | None: Returns either a list, or None if there
        were no matches to pattern.
    """
    result = re.findall(
        pattern=pattern,
        string=string,
        flags=re.I | re.M)
    logger.debug(
        "regex_findall(): %s original: '%s'", result, string)
    if len(result) > 0:
        return result
    return None


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
                values = (result, result)
                logger.debug(
                    "Retrieved values %s from string: %s", values, string)
                return values
            except ValueError:
                logger.exception("Could not convert to int: %s", result[0])
    logger.debug("Could not extract quantity from string: %s", string)
    return None


def parse_query_data(query: str, count: str, category: str) -> tuple:
    try:
        multiplier = 1
        if (count := count.strip("x")) == "":
            multiplier = abs(int(count))
    except ValueError:
        logger.exception("Could not convert multiplier to int")
        multiplier = 1
    quantity, unit = None, None
    if (data := get_quantity_from_string(query)) is not None:
        quantity, unit = data
    if category == "":  # Future checks here
        category = None
    return (multiplier, quantity, unit, category)


def process_queries(json: dict, store: tuple[str, str]) -> list[Item]:
    logger.debug("Parsing queries request JSON.")
    product_queries = []
    for query, count, category in zip(
            json["queries"], json["amounts"], json["categories"]):
        logger.debug("Parsing query: '%s'", query)
        if query in (None, ""):
            logger.debug("Parsed query was empty, skipping...")
            continue
        query_data = parse_query_data(query=query, count=count,
                                      category=category)
        item = Item(
            name=query,
            store=store,
            multiplier=query_data[0],
            quantity=query_data[1],
            unit=query_data[2],
            category=query_data[3])
        product_queries.append(item)

    logger.debug("Product queries len(%s)", len(product_queries))
    return product_queries


def create_product_list(response: Response,
                        query_item: Item) -> ProductList:
    products = ProductList(
        response=response,
        query=query_item)
    logger.debug(
        "Created ProductList from query string: '%s'", query_item.name)

    return products


@timer
def execute_product_search(query_data: list[Item],
                           store_id: int,
                           limit: int = 24) -> list[ProductList]:
    # TODO: ADD LOGGING
    responses = asyncio.run(api_fetch_products(
        store_id=str(store_id),
        product_queries=query_data,
        limit=limit))
    product_lists = []
    for r in responses:
        product_lists.append(create_product_list(*r))
    return product_lists


def parse_store_from_string(string: str) -> tuple[str | None, str | None]:
    """Find a store name and/or ID from a string using a RegEx pattern.

    Return results as a tuple.

    Args:
        string (str): String to parse.

    Returns:
        tuple[str | None, str | None]: Name and ID of store as strings.
    """
    data = regex_findall(
        r"\d+|^(?:\s*\b)\b[A-Za-z\s]+(?=\s?)", string)

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

    logger.debug("parse_store_from_string() -> ('%s', %s)", s_name, s_id)
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
        for i in stores:
            if i["name"].strip().lower() == str(query_data[0]).lower():
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


def execute_store_search(string: str) -> tuple[str, str] | None:
    """Parse, execute and validate a store search using a given string.

    Returns:
        tuple[str, str] | None: Store name and ID, None if not found.
    """
    logger.debug("Parsing store from string: '%s'", string)
    parsed_data = parse_store_from_string(string=string)
    if not any(parsed_data):
        return None
    logger.debug("Fetching store from api: %s", parsed_data)
    response = api_fetch_store(query_data=parsed_data)
    if not response:
        return None
    logger.debug("Parsing response from api: %s", response)
    return parse_and_validate_store(query_data=parsed_data,
                                    response=response)
