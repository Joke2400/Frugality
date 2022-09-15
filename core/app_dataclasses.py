from typing import NamedTuple
from dataclasses import dataclass
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
    basic_quantity_unit: str
    comparison_price: float
    comparison_unit: str


class ProductList:
    total_cost_cheapest = 0
    total_cost_expensive = 0
    total_cost_avg = 0
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
            basic_quantity_unit=i["basicQuantityUnit"],
            comparison_price=i["comparisonPrice"],
            comparison_unit=i["comparisonUnit"]
        ) for i in 
        self.response["data"]["store"]["products"]["items"]]
        
        self.max_priced_item = max(
            self.items, key=lambda x: x.comparison_price)

        self.min_priced_item = min(
            self.items, key=lambda x: x.comparison_price)

        self.avg_priced_item = sum(
            i.comparison_price for i in self.items) / len(self.items)

        self.max_prices.append(
            self.max_priced_item.comparison_price)
        self.min_prices.append(
            self.min_priced_item.comparison_price)
        self.avg_prices.append(
            self.avg_priced_item)

    @classmethod
    def update_total_cost(cls):
        cls.total_cost_cheapest = sum(cls.min_prices)
        cls.total_cost_expensive = sum(cls.max_prices)
        cls.total_cost_avg = sum(cls.avg_prices)
        
        
