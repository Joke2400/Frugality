from core import ProductList
from utils import LoggerManager as lgm
import re

logger = lgm.get_logger(name=__name__, level=20, stream=True)


def basic_regex(p: str, s: str) -> list[str]:
    result = re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)
    logger.debug(f"Regex result: {result}")
    return result


def validate_post(request) -> bool:
    if request.method == "POST":
        if request.json is None:
            return False
    return True


def get_quantity(s):
    r = basic_regex("(\d+)(l|k?gm?)", s)
    if len(r) == 0:
        return {"quantity": None, "unit": None}
    r = r[0]
    return {
        "quantity": int(r[0]) if r[0] != "" else None,
        "unit":     r[1] if r[1] != "" else None}


def get_specifiers(s):
    return basic_regex("laktoositon", s)


def print_results(results):
    ProductList.update_total_cost()
    for r in results:
        logger.info(r)
    logger.info(f"Min: {'': ^3}{ProductList.total_cheap:.2f}€")
    logger.info(f"Max: {'': ^3}{ProductList.total_expensive:.2f}€")
    logger.info(f"Avg: {'': ^3}{ProductList.total_avg:.2f}€\n")
