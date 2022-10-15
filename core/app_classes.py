from utils import LoggerManager as lgm
from typing import NamedTuple
from dataclasses import dataclass


logger = lgm.get_logger(name=__name__)


class AmountTuple(NamedTuple):
    amount: int
    quantity: int | None = None
    unit: str | None = None


@dataclass
class QueryItem:
    name: str
    amt: AmountTuple
    category: str | None = None
    must_contain: str | list[str] | None = None


@dataclass
class ResultItem:
    name: str
    amt: AmountTuple
    ean: str
    price: float
    quantity_unit: str
    cmp_price: float
    cmp_unit: str
    category: str | None = None


class ProductList:

    def __init__(self, response, query_string, category):
        self.query_string = query_string
        self.category = category
        self.items = self.parse_response(response=response)

        self.h_priced = max(
            self.items, key=lambda x: x.cmp_price)
        self.l_priced = min(
            self.items, key=lambda x: x.cmp_price)
        self.averaged = sum(
            i.cmp_price for i in self.items) / len(self.items)

    def parse_response(self, response):
        logger.debug(
            f"Parsing response for query '{self.query_string}'")
        items = [ResultItem(
            name=i["name"],
            ean=i["ean"],
            price=i["price"],
            quantity_unit=i["basicQuantityUnit"],
            cmp_price=i["comparisonPrice"],
            cmp_unit=i["comparisonUnit"]
        ) for i in response["data"]["store"]["products"]["items"]]
        logger.debug(
            f"Parsed {len(items)} items from response")
        return items

    def __str__(self):
        return f"\nQuery: {self.query_string}, Category: {self.category}\n" + \
               f"Cheapest:{'': ^10}{self.l_priced.cmp_price:.2f}{'':<2}€/" + \
               f"{self.l_priced.cmp_unit}{'':^3}{self.l_priced.name}\n" + \
               f"Most expensive:{'': ^4}{self.h_priced.cmp_price:.2f}" + \
               f"{'':<2}€/{self.h_priced.cmp_unit}{'':^3}" + \
               f"{self.h_priced.name}\n" + \
               f"Average price:{'': ^5}{self.averaged:.2f}{'':<2}€/" + \
               f"{self.l_priced.cmp_unit}\n"
