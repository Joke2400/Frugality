from typing import NamedTuple
from dataclasses import dataclass
    
class AmountTuple(NamedTuple):
    amount = int            # How many of the product does the user want?
    quantity = int = None   # How much (in a unit, eg: kg, g, L) does the user want?
    unit = str = None       # Unit of quantity

@dataclass
class QueryItem():
    name: str
    amt: AmountTuple
    category: str = None
    must_contain: str|list[str] = None

@dataclass
class ResultItem():
    name: str
    ean: str
    price: float
    basic_quantity_unit: str
    comparison_price: float
    comparison_unit: str