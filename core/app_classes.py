"""Contains classes for storing retrieved data."""

from dataclasses import dataclass
from dataclasses import field
from typing import Generator

from utils import LoggerManager


logger = LoggerManager.get_logger(name=__name__)


def convert_unit(unit: str) -> str:
    """Temporary helper function for converting units."""
    match unit:
        case "LTR":
            return "L"
        case "KGM":
            return "kg"
        case _:
            return unit


@dataclass(frozen=True, slots=True)
class ProductItem:
    """Dataclass for representing store products.

    Store field is important for determining which store
    to attribute the price data to.
    Fields are frozen to prevent accidental changes.
    """

    name: str
    count: int
    category: str
    ean: str
    store: tuple[str, str]
    comparison_unit: str
    comparison_price: int | float
    unit_price: int | float

    @property
    def total_price(self) -> int | float:
        """Compute total price of the desired amount of product."""
        return self.unit_price * self.count

    def dictify(self) -> dict:
        """Convert stored data to a dictionary and return it."""
        return {
            "name": self.name,
            "count": self.count,
            "category": self.category,
            "ean": self.ean,
            "store": self.store,
            "comparison_unit": self.comparison_unit,
            "comparison_price": self.comparison_price,
            "unit_price": self.unit_price
        }

    def __str__(self) -> str:
        """Return name and price/unit of item."""
        return f"{self.name} {self.comparison_price}€{self.comparison_unit}"


@dataclass(slots=True)
class ProductList:
    """Class that keeps track of a single product query for a store.

    Stores original query, response, store data and resulting products.
    Parses response and creates new ProductItem(s).
    Can return cheapest item and filter for products with matching
    quantity and/or string.
    """

    response: dict
    query_item: dict
    store: tuple[str, str]
    is_parsed: bool = False
    _items: list[ProductItem] = field(default_factory=list)

    @property
    def products(self) -> list[ProductItem]:
        """Return a list containing ProductItem(s).

        If response dict has not already been parsed,
        parse products from response, then return the list.
        """
        if not self.is_parsed:
            logger.debug("Parsing products for query: %s.",
                         self.query_item["query"])
            for i in self._parse():
                self._items.append(i)
            self.is_parsed = True
            logger.debug("Parsed %s products from response.",
                         len(self._items))
        return self._items

    @property
    def cheapest_item(self) -> ProductItem | None:
        """Return item from product list with lowest price/unit."""
        if len(self.products) == 0:
            return None
        values = (0, self.products[0])
        for inx, item in enumerate(self.products, start=1):
            if item.comparison_price < values[1].comparison_price:
                values = (inx, item)
        return values[1]

    def items_is_quantity(self, quantity: tuple[int | float, str]):
        """Todo: will return items with matching label_quantity."""
        pass

    def items_contains_string(self, string: str):
        """Todo: will return items with matching."""
        pass

    def _parse(self) -> Generator[ProductItem, None, None]:
        """Iterate through response data to create ProductItem instances.

        Yields:
            Generator[ProductItem]: Generator that yields ProductItems(s).
        """
        if (response_items := self._get_response_items()) is None:
            return None
        for i in response_items:
            item = self._create_product_item(item=i)
            if not item:
                continue
            yield item
        return None

    def _create_product_item(self, item: dict) -> ProductItem | None:
        """Create ProductItem from a dictionary.

        Args:
            item (dict): Response item dict.

        Returns:
            ProductItem | None: Returns None if a KeyError is raised.
        """
        try:
            product_item = ProductItem(
                name=item["name"],
                count=self.query_item["count"],
                category=item["hierarchyPath"][0]["slug"],
                ean=item["ean"],
                store=self.store,
                comparison_unit=convert_unit(item["comparisonUnit"]),
                comparison_price=item["comparisonPrice"],
                unit_price=item["price"])
        except KeyError as err:
            logger.exception(err)
            return None
        return product_item

    def _get_response_items(self) -> list[dict] | None:
        """Return items key from response dictionary.

        Returns:
            list[dict] | None: Returns None if KeyError or TypeError is raised.
        """
        try:
            _items = self.response["data"]["store"]["products"]["items"]
            if len(_items) == 0:
                return None
            return _items
        except (KeyError, TypeError) as err:
            logger.debug(err)
            return None

    def __str__(self):
        """Identify ProductList easily by it's query string."""
        return f"<ProductList query='{self.query_item['query']}'>"
