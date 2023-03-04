from utils import LoggerManager as lgm
from dataclasses import dataclass, field
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
    quantity: int
    unit: str
    category: str
    ean: str
    store: tuple[str, str]
    unit_price: int | float
    comparison_price: int | float

    @property
    def get_quantity(self) -> str:
        return f"{self.quantity}{self.unit}"

    @property
    def get_price(self) -> int | float:
        return self.unit_price

    @property
    def get_cmp_price(self) -> int | float:
        return self.comparison_price

    @property
    def get_total_price(self) -> int | float:
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
            self.items = self._parse()
            logger.debug("Parsed %s products from response.",
                         len(self.items))
        return self.items

    @property
    def cheapest_item(self) -> ProductItem:
        pass

    def _parse(self) -> list[ProductItem]:
        product_items = []
        if (response_items := self._get_response_items()) is not None:
            for i in response_items:
                try:
                    item = ProductItem(
                        name=i["name"],
                        count=self.query_item.count,
                        quantity=None,
                        unit=None,
                        category=self.query_item.category,
                        ean=i["ean"],
                        store=self.store,
                        unit_price=i["price"],
                        comparison_price=i["comparison_price"])
                    product_items.append(item)
                except KeyError as err:
                    logger.exception(err)
                    continue
        return product_items

    def _get_response_items(self) -> dict | None:
        try:
            items = self.response["data"]["store"]["products"]["items"]
            return items
        except KeyError as err:
            logger.exception(err)
            return None

    def __str__(self):
        return f"<ProductList query='{self.query_item.name}'>"
