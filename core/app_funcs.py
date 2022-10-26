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


def regex_findall(p: str, s: str) -> list[str] | None:
    result = re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)
    if len(result) != 0:
        logger.debug(f"Regex result: {result} ('{s}')")
        return result
    logger.debug(f"Regex result: 'None' ('{s}')")
    return None


def regex_get_quantity(s: str) -> list[float | None, str | None]:
    r = regex_findall(r"(\d+)(l|k?gm?)|(\d+)(l|k?\sgm?)", s)
    case = [None, None]
    if r is not None:
        tup = r[0]
        case = [
            float(tup[0]) if tup[0] != "" else None,
            tup[1] if tup[1] != "" else None
        ]                                       # Match statement here?
        if not case:       
            case = [
                float(tup[2]) if tup[2] != "" else None,
                tup[3] if tup[3] != "" else None
            ]
        if case[0] is not None:
            case[0] = case[0].replace(" ", "")
    return case


def parse_query_data(a: str, s: str) -> AmountData:
    try:
        amt = 1
        if a is not None and a != "":
            amt = abs(int(a))
            if amt > 100:
                amt = 100
    except ValueError:
        logger.exception(
            "'amt' could not be converted to 'int'")
        amt = 1
    if isinstance(s, str):
        q, u = regex_get_quantity(s)
    return AmountData(q, u, amt)


def extract_request_json(request) -> tuple[list, list, list]:
    logger.debug(
        "Extracting request JSON...")
    return (
        request.json["queries"],
        request.json["amounts"],
        request.json["categories"])
    # TODO: Add some input validation


def parse_input(data: tuple[list, list, list]) -> list[QueryItem]:
    logger.debug("Parsing request JSON...")
    product_queries = []

    for query, amt, cat in zip(
            data[0], data[1], data[2]):

        logger.debug(f"Parsing new query: '{query}'")
        if query is None or query == "":
            logger.debug("Parsed query was empty, skipping...")
            continue

        amount_data = parse_query_data(a=amt, s=query)
        if cat == "":
            cat = None
        product_queries.append(
            QueryItem(name=query, amount=amount_data, category=cat))
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
