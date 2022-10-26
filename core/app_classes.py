from re import L
from utils import LoggerManager as lgm
from dataclasses import dataclass
from requests import Response


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
    def price_per_unit(self) -> str:
        return f"{self.price.cmp_price}/{self.amount.unit}"

    def __str__(self) -> str:
        return f"[Name]: '{self.name}'\n" \
               f"[EAN]: {self.ean}\n" + \
               f"[Quantity]: {self.amount}\n" + \
               f"[Price]: {self.price}\n" + \
               f"[Price/Unit]: {self.price_per_unit}"


@dataclass
class ProductList:
    response: Response
    query: tuple[str, int]  # (query string, amount)
    store_id: str
    category: str | None

    def __post_init__(self):
        logger.debug(f"Parsing response for query '{self.query[0]}'")
        self.items = [ProductItem(
            name=i["name"],
            ean=i["ean"],
            category=self.category,
            amount=AmountData(i["basicQuantityUnit"],
                              i["comparisonUnit"],
                              self.query[1]),
            price=PriceData(i["price"],
                            i["comparisonPrice"]))
            for i in self.response["data"]["store"]["products"]["items"]]
        logger.debug(f"Parsed '{len(self.items)}' items from response")

    @property
    def highest_price(self) -> tuple[str, int | float, int | float]:
        i = max(self.items, key=lambda x: x.price.cmp_price)
        return (i.name, i.price.cmp_price, i.amount.unit)

    @property
    def lowest_price(self) -> tuple[str, int | float, int | float]:
        i = min(self.items, key=lambda x: x.price.cmp_price)
        return (i.name, i.price.cmp_price, i.amount.unit)

    @property
    def average_price(self) -> tuple[str, int | float, int | float]:
        i = sum(i.price.cmp_price for i in self.items) / len(self.items)
        return i

    def __str__(self) -> str:
        hi = self.highest_price
        lo = self.lowest_price
        av = self.average_price

        return f"{'': ^3}Query: {self.query[0]}, +" + \
               f"Category: {self.category}\n" + \
               f"\nHighest price:{'': ^8}'{hi[0]}' " + \
               f"{'': ^5}Price/unit:{hi[1]:.2f}€/{hi[2]}\n" + \
               f"Lowest price:{'': ^8}'{lo[0]}' " + \
               f"{'': ^5}Price/unit: {lo[1]:.2f}€/{lo[2]}\n" + \
               f"Average price:{'': ^8}'{self.query[0]}' " + \
               f"{'': ^5}Price/unit: {av:.2f}€/{lo[2]}\n\n"
