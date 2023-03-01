from utils import LoggerManager as lgm
from dataclasses import dataclass, field
from typing import Optional
from requests import Response
import core

logger = lgm.get_logger(name=__name__)


@dataclass(frozen=True, slots=True)
class Item:
    """
    A basic item, may represent either
    user queries or received and parsed results.

    name: Non-optional, descriptor-validator to be added
    ean: Product ean id, can be used in product searches, google it
    category: Category as a string, this is not a pretty string to print

    quantity: Quantity of product in a single packaging as an integer
    unit: The unit that the quantity is given in
    comparison_unit: The ???

    store: Store data, name and id
    unit_price: The price for a single product
    comparison_price: The price for a product / unit

    multiplier: Multiplier used for calculating the total cost, user-defined
    """

    # Identifying data
    name: str
    ean: str | None = None
    category: str | None = None

    # Product-specific data
    quantity: int | None = None
    unit: str | None = None
    comparison_unit: str | None = None

    # Store-specific data
    store: Optional[tuple[str, str]] = None
    unit_price: Optional[int | float] = None
    comparison_price: Optional[int | float] = None

    # <User-defined data
    multiplier: int = 1

    @property
    def quantity_string(self) -> str:
        return f"{self.quantity}{self.unit}"

    @property
    def total_price(self) -> int | float | None:
        if self.unit_price is None:
            return None
        return self.multiplier * self.unit_price


@dataclass
class ProductList:
    response: Response
    query: Item
    items: list[Item] = field(default_factory=list)

    def __post_init__(self):
        self.store = self.query.store
        self.category = self.query.category

    @property
    def products(self) -> list[Item]:
        if len(self.items) == 0:
            logger.debug("Product list empty, parsing response...")
            self.items = self._parse()
        logger.debug(f"Returning {len(self.items)} products.")
        return self.items

    def _parse(self) -> list[Item]:
        logger.debug(f"Parsing response for query '{self.query.name}'")
        items = []
        for i in self.response["data"]["store"]["products"]["items"]:
            q, u = core.regex_get_quantity(i["name"])  # 'quantity' 'unit'
            item = Item(
                name=i["name"],
                ean=i["ean"],
                category=self.category,
                quantity=q,
                unit=u,
                comparison_unit=i["comparisonUnit"],
                store=self.store,
                unit_price=i["price"],
                comparison_price=i["comparisonPrice"],
                multiplier=self.query.multiplier)
            items.append(item)
        return items
