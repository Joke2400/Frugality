from utils import LoggerManager as lgm
from core import AmountData, QueryItem, ProductList
from requests import Response
import re

logger = lgm.get_logger(name=__name__)

# Might want to create classes instead of a functional
# approach for organizational purposes.
# But then again, who likes making boilerplate?


def validate_post(request) -> bool:
    if request.method == "POST":
        if request.json is not None:
            return True
    return False
    # TODO: Add some input validation


def extract_request_json(request) -> tuple[list, list, list]:
    logger.debug(
        "Extracting request JSON...")
    return (
        request.json["queries"],
        request.json["amounts"],
        request.json["categories"])
    # TODO: Add some input validation


def regex_findall(p: str, s: str) -> list[tuple[str, str]] | None:
    result = re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)
    logger.debug(f"Regex result: {result} ('{s}')")
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


def parse_input(data: tuple[list, list, list]) -> list[QueryItem]:
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
                      amount=amount_data,
                      category=cat))

    logger.debug(f"Product queries len({len(product_queries)})\n")
    return product_queries


def parse_response(response: Response, query_item: QueryItem,
                   request_params: dict):
    store_id = request_params["variables"]["StoreID"]
    category = request_params["variables"]["slugs"]

    products = ProductList(
        response=response,
        query=query_item,
        store_id=store_id,
        category=category)
    logger.debug(f"Created ProductList from query string: '{query_item.name}'")

    return products
