from utils import LoggerManager as lgm
from dataclasses import dataclass
from requests import Response
import core

logger = lgm.get_logger(name=__name__)


@dataclass
class AmountData:
    quantity: int | None
    unit: str | None
    multiplier: int = 1

    def __str__(self) -> str:
        return f"{self.multiplier} x {self.quantity}{self.unit}"


@dataclass
class PriceData:
    unit_price: int | float  # Basic price
    cmp_price: int | float  # Comparison price (value for price/unit)

    def __str__(self) -> str:
        return f"{self.unit_price}"


@dataclass
class QueryItem:
    name: str
    amount: AmountData
    category: str | None

    def __str__(self) -> str:
        return f"[Name]: '{self.name}'\n" \
               f"[Quantity]: {self.amount}"


@dataclass
class ProductItem:
    name: str
    amount: AmountData
    category: str | None
    ean: str
    price: PriceData

    @property
    def total_price(self) -> str:
        price = self.amount.multiplier * self.price.unit_price
        return f"{self.amount.multiplier}x for " + \
               f"{price:.2f}€"

    @property
    def price_per_unit(self) -> str:
        return f"{self.price.unit_price:.2f}€ for {self.amount.quantity}(s)"

    @property
    def price_per_unit_quantity(self) -> str:
        return f"{self.price.cmp_price:.2f}€/{self.amount.unit}"

    def __str__(self) -> str:
        return f"[Name]: '{self.name}'\n" \
               f"[EAN]: {self.ean}\n" + \
               f"[Quantity]: {self.amount}\n" + \
               f"[Price]: {self.price_per_unit}\n" + \
               f"[Price/unit]: {self.price_per_unit_quantity}\n" + \
               f"[Total price]: {self.total_price}\n"


@dataclass
class ProductList:
    response: Response
    query: QueryItem
    store_id: str
    category: str | None

    def __post_init__(self):
        logger.debug(f"Parsing response for query '{self.query.name}'")
        self.items = [ProductItem(
            name=i["name"],
            ean=i["ean"],
            category=self.category,
            amount=AmountData(core.regex_get_quantity(i["name"])[0],
                              i["comparisonUnit"],
                              self.query.amount.multiplier),
            price=PriceData(float(i["price"]),
                            float(i["comparisonPrice"])))
            for i in self.response["data"]["store"]["products"]["items"]]
        logger.debug(f"Parsed '{len(self.items)}' items from response")

    @property
    def highest_price(self) -> ProductItem:
        i = max(self.items, key=lambda x: x.price.cmp_price)
        return i

    @property
    def lowest_price(self) -> ProductItem:
        i = min(self.items, key=lambda x: x.price.cmp_price)
        return i

    @property
    def average_price(self) -> tuple[str, int | float, int | float]:
        i = sum(i.price.cmp_price for i in self.items) / len(self.items)
        return i

    def __str__(self) -> str:
        hi = self.highest_price
        lo = self.lowest_price
        av = self.average_price

        return f"\n[Query: {self.query.name}]\t" + \
               f"[Category: {self.category}]\n" + \
               f"\nHighest price:{'': ^5}Price/unit: " + \
               f"{hi.price_per_unit_quantity}{'': ^4}'{hi.name}'" + \
               f"\nLowest price:{'': ^6}Price/unit: " + \
               f"{lo.price_per_unit_quantity}{'': ^4}'{lo.name}'\n"