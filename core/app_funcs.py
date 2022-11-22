from utils import timer, LoggerManager as lgm
from core import AmountData, QueryItem, ProductList
from api import api_fetch_products, api_get_store
from requests import Response

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


def parse_query_data(a: str, s: str | None = None) -> AmountData:
    quantity, unit, quantity_str = None, None, ""
    if isinstance(s, str):
        quantity, unit = regex_get_quantity(s)
        if quantity is not None and unit is not None:
            quantity_str = str(quantity).strip("x")
            quantity_str = str(quantity) + unit

    try:
        multiplier = 1
        if a is not None and a != "":
            multiplier = abs(int(float(a)))
            if multiplier > 100:
                multiplier = 100
    except ValueError:
        logger.exception("Could not convert to 'int'")
        multiplier = 1

    data = AmountData(quantity=quantity,
                      unit=unit,
                      multiplier=multiplier,
                      quantity_str=quantity_str)
    logger.debug(f"AmountData: {data}")
    return data


def parse_input(data: tuple[list, list, list],
                store: tuple[str | None, int | None]) -> list[QueryItem]:
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
            QueryItem(name=query,
                      store=store,
                      amount=amount_data,
                      category=cat))

    logger.debug(f"Product queries len({len(product_queries)})\n")
    return product_queries


def create_product_list(response: Response, query_item: QueryItem):
    products = ProductList(
        response=response,
        query=query_item)
    logger.debug(f"Created ProductList from query string: '{query_item.name}'")

    return products


def parse_store_data(store_str: str) -> tuple[str | None, int | None] | None:
    s_name, s_id = None, None
    data = regex_findall(
        r"\d+|^(?:\s*\b)\b[A-Za-z\s]+(?=\s?)", store_str)

    if data is not None and not isinstance(data[0], tuple):
        if len(data) == 2:
            s_name = str(data[0]).strip()
            logger.debug(f"store_info: name = {s_name}")
            try:
                s_id = int(str(data[1]).strip())
                logger.debug(f"store_info: name = {s_id}")
            except ValueError:
                logger.debug("Could not convert ID to int")
        if len(data) == 1:
            try:
                s_id = int(str(data[0]).strip())
            except ValueError:
                s_name = str(data[0]).strip()

    if s_name is None and s_id is None:
        logger.debug("Regex returned no results.")
        return None
    logger.debug(f"Regex result: '{s_name}' '{s_id}'")
    return (s_name, s_id)

# TODO: ADD LOGGING
@timer
def execute_product_search(query_data: list[QueryItem],
                           store_id: int,
                           limit: int = 24) -> list[ProductList]:
    responses = asyncio.run(api_fetch_products(
        store_id=str(store_id),
        product_queries=query_data,
        limit=limit))

    product_lists = []
    for r in responses:
        product_lists.append(create_product_list(*r))

    return product_lists

# TODO: IMPLEMENT, ADD LOGGING
@timer
def validate_store_data(store_data):
    return store_data
    '''
    # PUT IN FUNCTION --------------------------
    if store_data is None:
        # No store data available
        # TODO: Prompt user for store or address
        return {
            "data": "[ERROR]: Store name or id must be specified for now."
            }
    if store_data[0] is None:
        pass
    if store_data[1] is None:
        # Store name available
        api_get_store(store_data[0])

    # ---------------------------
    '''

# TODO: IMPLEMENT, ADD LOGGING
def save_product_data():
    pass  # Database will be the responsibility of DataManager

# TODO: ADD LOGGING
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
