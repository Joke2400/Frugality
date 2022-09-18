from core import ProductList
import re


def basic_regex(p: str, s: str) -> list[str]:
    return re.findall(
        pattern=p,
        string=s,
        flags=re.I | re.M)


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
        print(r)
    print(f"Min: {'': ^3}{ProductList.total_cheap:.2f}€")
    print(f"Max: {'': ^3}{ProductList.total_expensive:.2f}€")
    print(f"Avg: {'': ^3}{ProductList.total_avg:.2f}€")
    print("")
