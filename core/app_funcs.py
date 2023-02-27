from utils import timer, LoggerManager as lgm
from core import Item, ProductList
from api import api_fetch_products, api_fetch_store
from requests import Response
from typing import Optional, Any

import asyncio
import re

logger = lgm.get_logger(name=__name__)


def extract_request_json(request) -> tuple[list, list, list]:
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        tuple[list, list, list]: _description_
    """    
    logger.debug(
        "Extracting request JSON...")
    return (
        request.json["queries"],
        request.json["amounts"],
        request.json["categories"])


def regex_search(pattern: str, string: str
                 ) -> re.Match[str] | None:
    """
    Scan through a string and return a single match
    to the given pattern. Returns a Match object if a
    match is found, returns None otherwise.

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
    logger.debug(f"regex_search: {result} (str: '{string}')")
    return result


def regex_findall(pattern: str, string: str
                  ) -> list | None:
    result = re.findall(
        pattern=pattern,
        string=string,
        flags=re.I | re.M)
    logger.debug(f"regex_findall: {result} original_str: '{string}'")
    if len(result) > 0:
        return result
    return None


def regex_get_quantity(s: str) -> tuple[int, str] | tuple[None, None]:
    r = regex_findall(r"(\d+)\s?(l|kg|g)", s)
    empty = (None, None)
    if r is not None:
        v = r[0]
        tup = (int(v[0]), v[1])
        logger.debug(f"Quantity tuple: {tup}")
        return tup
    logger.debug(f"Quantity tuple: {empty}")
    return empty


def parse_query_data(a: str, s: str | None = None
                     ) -> tuple[int | None, str | None, int]:
    quantity, unit = None, None
    if isinstance(s, str):
        quantity, unit = regex_get_quantity(s)
    try:
        multiplier = 1
        if a not in ("", None):
            a = a.strip("x")
            multiplier = abs(int(float(a)))
            if multiplier > 100:
                multiplier = 100
    except ValueError:
        logger.exception("Could not convert to 'int'")
        multiplier = 1
    data = (quantity, unit, multiplier)
    logger.debug(f"AmountData: {data}")
    return data


def parse_input(data: tuple[list, list, list],
                store: Optional[tuple[str, int]]) -> list[Item]:
    logger.debug("Parsing request JSON...")
    product_queries = []

    for query, amt, cat in zip(
            data[0], data[1], data[2]):
        logger.debug(f"Parsing new query: '{query}'")
        if query is None or query == "":
            logger.debug("Parsed query was empty, skipping...")
            continue
        if cat == "":
            cat = None
        amount_data = parse_query_data(a=amt, s=query)
        product_queries.append(
            Item(name=query,
                 store=store,
                 quantity=amount_data[0],
                 unit=amount_data[1],
                 multiplier=amount_data[2],
                 category=cat))

    logger.debug(f"Product queries len({len(product_queries)})\n")
    return product_queries


def create_product_list(response: Response,
                        query_item: Item) -> ProductList:
    products = ProductList(
        response=response,
        query=query_item)
    logger.debug(f"Created ProductList from query string: '{query_item.name}'")

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
                logger.debug(err)
            if i := is_digits(data[1]):
                s_id = i

        case [str()] as data:
            if i := is_digits(data[0]):
                s_id = i
            else:
                try:
                    s_name = str(data[0]).strip()
                except ValueError as err:
                    logger.debug(err)
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
            logger.debug(err)
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
        logger.debug(err)
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
