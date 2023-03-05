from utils import LoggerManager as lgm
from dataclasses import dataclass, field
from typing import Generator
import core

logger = lgm.get_logger(name=__name__)


@dataclass(frozen=True, slots=True)
class QueryItem:
    name: str
    count: int
    quantity: int | None
    unit: str | None
    category: str | None


@dataclass(frozen=True, slots=True)
class ProductItem:
    name: str
    count: int
    category: str
    ean: str
    store: tuple[str, str]
    comparison_unit: str
    comparison_price: int | float
    unit_price: int | float
    label_quantity: int | None
    label_unit: str | None

    @property
    def total_price(self) -> int | float:
        return self.unit_price * self.count


@dataclass(slots=True)
class ProductList:
    response: dict
    query_item: QueryItem
    store: tuple[str, str]
    items: list[ProductItem] = field(default_factory=list)

    @property
    def products(self) -> list[ProductItem]:
        if len(self.items) == 0:
            logger.debug("Parsing products for query: %s.",
                         self.query_item.name)
            for i in self._parse():
                self.items.append(i)
            logger.debug("Parsed %s products from response.",
                         len(self.items))
        return self.items

    @property
    def cheapest_item(self) -> ProductItem | None:
        if (response_items := self._get_response_items()) is not None:
            values = (0, response_items[0])
            for inx, item in enumerate(response_items[1:], start=1):
                if item["comparisonPrice"] < values[1]["comparisonPrice"]:
                    values = (inx, item)
            item = self._create_product_item(item=values[1])
            response_items.pop(values[0])
            return item
        return None

    def _parse(self) -> Generator[ProductItem, None, None]:
        if (response_items := self._get_response_items()) is None:
            return None
        for i in response_items:
            item = self._create_product_item(item=i)
            if not item:
                continue
            yield item
        return None

    def _create_product_item(self, item: dict) -> ProductItem | None:
        try:
            quantity, unit = None, None
            if (data := core.get_quantity_from_string(
                    string=item["name"])) is not None:
                quantity, unit = data
            product_item = ProductItem(
                name=item["name"],
                count=self.query_item.count,
                category=item["hierarchyPath"][0]["slug"],
                ean=item["ean"],
                store=self.store,
                comparison_unit=item["comparisonUnit"],
                comparison_price=item["comparisonPrice"],
                unit_price=item["price"],
                label_quantity=quantity,
                label_unit=unit)
        except KeyError as err:
            logger.exception(err)
            return None
        return product_item

    def _get_response_items(self) -> dict | None:
        try:
            items = self.response["data"]["store"]["products"]["items"]
            return items
        except KeyError as err:
            logger.exception(err)
            return None

    def __str__(self):
        return f"<ProductList query='{self.query_item.name}'>"
