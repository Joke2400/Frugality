from typing import NamedTuple
from unicodedata import category

class QueryItem(NamedTuple):
    name: str
    amt: tuple[int, int|None, str|None]
    category: str = None
    must_contain: str|list[str] = None

class ResultItem(NamedTuple):
    name: str
    ean: str
    price: float
    basic_quantity_unit: str
    comparison_price: float
    comparison_unit: str