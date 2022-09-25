from utils import LoggerManager as lgm
import core
import re


logger = lgm.get_logger(name=__name__)


def basic_regex(p: str, s: str) -> list[str] | None:
    result = re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)
    if len(result) != 0:
        logger.debug(f"Regex result: {result} ('{s}')")
        return result
    return None


def validate_post(request) -> dict | None:
    if request.method == "POST":
        if request.json is not None:
            return request.json
    return None


def get_quantity(s: str):
    if isinstance(s, str):
        r = basic_regex(r"(\d+)(l|k?gm?)", s)
        if r is not None:
            r = r[0]
            return {
                "quantity": int(r[0]) if r[0] != "" else None,
                "unit":     r[1] if r[1] != "" else None}
    return {"quantity": None, "unit": None}


def get_specifiers(s):
    # TODO: Rename function
    # TODO: Replan concept behind must_contain variable
    return basic_regex("laktoositon", s)


def parse_input(request):
    logger.debug(
        "Parsing request JSON...")
    product_queries = []
    for query, amt, cat in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
        if query == "" or query is None:
            logger.debug(
                "Parsed query was empty, skipping...")
            continue
        logger.debug(
            f"Parsing new query: '{query}'")

        try:
            if amt != "" and amt is not None:
                amt = abs(int(amt))
                if amt > 100:
                    amt = 100
            else:
                amt = 1
        except ValueError:
            logger.exception(
                "Amt could not be converted to 'int'")
            amt = 1
        tup = core.AmountTuple(amount=amt, **get_quantity(query))
        contain = get_specifiers(query)

        product_queries.append(
            core.QueryItem(
                name=query,
                amt=tup,
                category=cat,
                must_contain=contain))

    logger.debug(
        f"Product queries len({len(product_queries)})\n")
    return product_queries