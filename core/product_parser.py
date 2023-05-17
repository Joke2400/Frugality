"""Contains classes for storing retrieved data."""

from typing import Generator
from dataclasses import dataclass
from dataclasses import field

from utils import LoggerManager

from .store import Store
from .product import Product
from .product import PriceData


logger = LoggerManager.get_logger(name=__name__)


@dataclass(slots=True)
class ProductQueryParser:
    """Class that keeps track of store, query and response results.

    TODO: Rest of this docstring.
    """

    response: dict
    query: dict
    store: Store

    _items: list[Product] = field(default_factory=list)
    _is_parsed: bool = False

    @property
    def products(self) -> list[Product]:
        """Return a list containing Product(s)."""
        if self._is_parsed:
            return self._items
        logger.debug("Parsing products for query: %s.",
                     self.query["query"])
        for i in self._parse():
            self._items.append(i)
        self._is_parsed = True
        logger.debug("Parsed %s products from response.",
                     len(self._items))
        return self._items

    def _parse(self) -> Generator[Product, None, None]:
        """Iterate through response data to create Product instances.

        Yields:
            Generator[Product]: Generator that yields Product(s).
        """
        if (items := self._fetch_response_items()) is None:
            return None
        for i in items:
            item = self._create_product_item(i)
            if not item:
                continue
            yield item
        return None

    def _fetch_response_items(self) -> list[dict] | None:
        """Return items key from stored response."""
        try:
            _items = self.response["data"]["store"]["products"]["items"]
            if len(_items) == 0:
                return None
            return _items
        except (KeyError, TypeError) as err:
            logger.debug(err)
            return None

    def _create_product_item(self, i: dict) -> Product | None:
        """Create a Product instance from a dictionary.

        Returns:
            Product | None: Returns None if a KeyError is raised.
        """
        try:
            price_data = PriceData(
                price=i["price"],
                basic_quantity_unit=self.reformat_unit(i["basicQuantityUnit"]),
                comparison_price=i["comparisonPrice"],
                comparison_unit=self.reformat_unit(i["comparisonUnit"])
            )
            product = Product(
                ean=i["ean"],
                slug=i["slug"],
                name=i["name"],
                brand_name=i["brandName"],
                category=i["hierarchyPath"][0]["name"],
                category_str_path=i["hierarchyPath"][0]["slug"],
                store=self.store,
                price_data=price_data
            )
        except KeyError as err:
            logger.exception(err)
            return None
        return product

    def reformat_unit(self, unit: str) -> str:
        """Reformat a unit string."""
        match unit:
            case "LTR":
                return "L"
            case "KGM":
                return "kg"
            case _:
                return unit

    def dictify(self) -> dict:
        """Return query, store and products as a single dict."""
        products = []
        for i in self.products:
            products.append(i.dictify())
        return {
            "query": self.query,
            "store": self.store.data,
            "products": products
        }

    def cheapest_item(self) -> Product | None:
        """Return item with lowest price per unit."""
        if len(self.products) == 0:
            return None
        values = (0, self.products[0])
        for inx, item in enumerate(self.products, start=1):
            if (item.price_data.comparison_price <
                    values[1].price_data.comparison_price):
                values = (inx, item)
        return values[1]

    def __str__(self):
        """Return human-readable name for class."""
        return f"<ProductQueryParser query='{self.query['query']}'>"
