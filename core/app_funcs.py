from utils import LoggerManager as lgm
from core import AmountTuple, QueryItem
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


def parse_query_data(a: str, s: str) -> AmountTuple:
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

    q, u = None, None
    if isinstance(s, str):
        r = regex_findall(r"(\d+)(l|k?gm?)", s)
        if r is not None:
            f = r[0]  # We're interested only in the first result
            q = int(f[0]) if f[0] != "" else None
            u = f[1] if f[1] != "" else None
    return AmountTuple(amt, q, u)


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

        query_data = parse_query_data(a=amt, s=query)
        if cat == "":
            cat = None
        product_queries.append(
            QueryItem(name=query, amt=query_data, category=cat))
    logger.debug(f"Product queries len({len(product_queries)})\n")
    return product_queries
