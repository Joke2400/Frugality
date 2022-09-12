from typing import NamedTuple

class QueryItem(NamedTuple):
    query: str      # Query
    amt: str = None    # User-defined amount, ex: 1L of drink, 500g of meat etc etc
    category: str = None   # Ex. Vegetables, chicken, dairy products etc (skaupats categories)

class ResultItem(NamedTuple):
    pass