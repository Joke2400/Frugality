from utils import timer, LoggerManager as lgm
from core import Item, ProductList
from api import api_fetch_products, api_get_store
from requests import Response
from typing import Optional, Any

import asyncio
import re

logger = lgm.get_logger(name=__name__)


def validate_post(request) -> bool:
    # https://flask.palletsprojects.com/en/2.2.x/security/
    if request.method == "POST":
        if request.json is not None:
            return True
    return False
    # TODO: Add some input validation


def extract_request_json(request) -> tuple[list, list, list]:
    # https://flask.palletsprojects.com/en/2.2.x/security/
    logger.debug(
        "Extracting request JSON...")
    return (
        request.json["queries"],
        request.json["amounts"],
        request.json["categories"])
    # TODO: Add some input validation


def regex_findall(p: str, s: str
                  ) -> list[tuple[str, str]] | list[str] | None:
    result = re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)
    logger.debug(f"Regex result: {result} (Original str: '{s}')")
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


def parse_store_input(store_str: str) -> tuple[str | None, str | None]:
    data = regex_findall(
        r"\d+|^(?:\s*\b)\b[A-Za-z\s]+(?=\s?)", store_str)

    def is_digits(string: Any) -> bool:
        try:
            int(str(string).strip())
        except ValueError:
            return False
        return True

    s_name, s_id = None, None
    match data:
        # Case where both values are given
        case [str(), str()] as data:
            s_name = str(data[0]).strip()
            # Ensuring that the ID actually consists of digits
            if is_digits(data[1]):
                s_id = str(data[1]).strip()

        # In other cases we try to convert the single string into an int
        # If that fails it's presumed that a name was given instead of an id
        case [str()] as data:
            if is_digits(data[1]):
                s_id = str(data[1]).strip()
            else:
                s_name = str(data[0]).strip()
        # All other cases
        case _:
            logger.debug("Regex returned no results.")
            return None, None

    logger.debug(f"parse_store_input: '{s_name}' '{s_id}'")
    return (s_name, s_id)


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


def get_store_data(store_data: tuple[str | None, int | None] | None
                   ) -> Response | None:
    match store_data:
        # Allowed cases are (None, str) or (str, None) or (str, str)
        case (None, str()) | (str(), str()) as store_data:
            value = store_data[1]
            logger.debug(f"Store ID found, using Store ID: '{value}'")
            response = api_get_store(store_id=value)
            return response

        case (str(), None) as store_data:
            value = store_data[0]
            logger.debug(f"Store name found, using Store name: '{value}'")
            response = api_get_store(store_name=value)
            return response

        case _:
            logger.debug("Store tuple can not be empty.")
            return None


def validate_store_data(response: Response,
                        store_data: tuple[str | None, int | None] | None
                        ) -> tuple[str, str] | None:
    # TODO: ADD LOGGING
    store_name, store_id = store_data

    if store_id in ("", None):
        if response["data"]["searchStores"]["totalCount"] == 0:
            return None
        stores = response["data"]["searchStores"]["stores"]
        store = None
        for i in stores:
            if i["id"] == store_id or i["name"] == store_name:
                store = i
                break
        if i is None:
            return None
    else:
        store = response["data"]["store"]
    store_data = (store.get("name"), store.get("id"))
    if store_data[0] is None and store_data[1] is None:
        return None
    return store_data


def products_overview(product_lists: list[ProductList]):
    for pl in product_lists:
        p_len = len(pl.products)
        logger.info(f"Products found: {p_len}.")
        f_str = pl.query.amount.quantity  # Maybe set filter to this value as default, then add a apply filter func

        if f_str not in (None, ""):
            pl.set_filter(str(f_str))
            f_len = len(pl.products)
            logger.info(
                f"Excluding products that do not contain: '{f_str}'.")
            logger.info(f"Filtered out {p_len - f_len} products. " +
                        f"Remaining products: {f_len}.")
        logger.info(pl)


# TODO: IMPLEMENT, ADD LOGGING
def save_product_data():
    pass  # Database will be the responsibility of DataManager
