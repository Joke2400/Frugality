from typing import NamedTuple
from dataclasses import dataclass
from utils import timer
import json
    
class AmountTuple(NamedTuple):
    amount: int
    quantity: int = None
    unit: str = None

@dataclass
class QueryItem:
    name: str
    amt: AmountTuple
    category: str = None
    must_contain: str|list[str] = None

@dataclass
class ResultItem:
    name: str
    ean: str
    price: float
    quantity_unit: str
    cmp_price: float
    cmp_unit: str


class ProductList:
    total_cheap = 0
    total_expensive = 0
    total_avg = 0
    avg_prices = []
    min_prices = []
    max_prices = []
    
    def __init__(self, response, query_string, category):
        self.query_string = query_string
        self.category = category
        self.response = json.loads(response.text)
        self.items = [ResultItem(
            name=i["name"],
            ean=i["ean"],
            price=i["price"],
            quantity_unit=i["basicQuantityUnit"],
            cmp_price=i["comparisonPrice"],
            cmp_unit=i["comparisonUnit"]
        ) for i in 
        self.response["data"]["store"]["products"]["items"]]
        self.closest = self.items[0]
        
        self.highest = max(
            self.items, key=lambda x: x.cmp_price)

        self.lowest = min(
            self.items, key=lambda x: x.cmp_price)

        self.avg = sum(
            i.cmp_price for i in self.items) / len(self.items)

        self.max_prices.append(
            self.highest.cmp_price)
        self.min_prices.append(
            self.lowest.cmp_price)
        self.avg_prices.append(
            self.avg)

    @classmethod
    def update_total_cost(cls):
        cls.total_cheap = sum(cls.min_prices)
        cls.total_expensive = sum(cls.max_prices)
        cls.total_avg = sum(cls.avg_prices)
    
    def __str__(self):
        return \
        f"""Query: {self.query_string}, Category: {self.category}
        Cheapest:{'': ^10}{self.lowest.cmp_price:.2f}{'':<2}€/{self.lowest.cmp_unit}\
            {'':^3}{self.lowest.name}
        Most expensive:{'': ^4}{self.highest.cmp_price:.2f}{'':<2}€/{self.highest.cmp_unit}\
            {'':^3}{self.highest.name}
        Average price:{'': ^5}{self.avg:.2f}{'':<2}€/{self.lowest.cmp_unit}
        """
        
