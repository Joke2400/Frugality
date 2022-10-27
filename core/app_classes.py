from utils import LoggerManager as lgm
from dataclasses import dataclass, field
from requests import Response
import core

logger = lgm.get_logger(name=__name__)


@dataclass
class AmountData:
    quantity: float | None
    unit: str | None
    multiplier: int = 1
    quantity_str: str = ""

    def __str__(self) -> str:
        return f"{self.multiplier} x {self.quantity_str}"


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
        return f"{self.price.unit_price:.2f}€ for {self.amount.quantity_str}"

    @property
    def price_per_unit_quantity(self) -> str:
        return f"{self.price.cmp_price:.2f}€/{self.amount.unit}"

    def __str__(self) -> str:
        return f"\n[Name]: '{self.name}'\n" \
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
    items: list[ProductItem] = field(default_factory=list)
    filtered: bool = False

    def parse(self) -> None:
        self.items = []
        logger.debug(f"Parsing response for query '{self.query.name}'")
        for i in self.response["data"]["store"]["products"]["items"]:
            q, u = core.regex_get_quantity(i["name"])
            s = ""
            if q is not None and u is not None:
                s = str(q) + u
            a = AmountData(
                quantity=q,
                unit=i["comparisonUnit"],
                multiplier=self.query.amount.multiplier,
                quantity_str=s)

            p = PriceData(
                float(i["price"]),
                float(i["comparisonPrice"]))

            item = ProductItem(
                name=i["name"],
                ean=i["ean"],
                category=self.category,
                amount=a,
                price=p)

            self.items.append(item)
        logger.debug(f"Parsed '{len(self.items)}' items from response")

    def _overview(self, filtered=False):
        self.filtered = False
        if filtered:
            self.filtered = True
        if len(self.items) == 0:
            self.parse()

        hi = self.highest_price
        lo = self.lowest_price
        av = self.average_price
        return hi, lo, av

    @property
    def products(self) -> list[ProductItem]:
        if len(self.items) == 0:
            self.parse()
        return self.items

    @property
    def filtered_products(self) -> list[ProductItem]:
        f = self.query.amount.quantity
        filtered = []
        for i in filter(lambda p: p.amount.quantity == f, self.products):
            filtered.append(i)
        return filtered

    @property
    def highest_price(self) -> ProductItem:
        items = self.products
        if self.filtered:
            items = self.filtered_products
        i = max(items, key=lambda x: x.price.cmp_price)
        return i

    @property
    def lowest_price(self) -> ProductItem:
        items = self.products
        if self.filtered:
            items = self.filtered_products
        i = min(items, key=lambda x: x.price.cmp_price)
        return i

    @property
    def average_price(self) -> float:
        items = self.products
        if self.filtered:
            items = self.filtered_products
        i = sum(i.price.cmp_price for i in items) / len(items)
        return i

    def __str__(self) -> str:
        hi, lo, av = self._overview(filtered=False)
        return f"\n\nQuery: '{self.query.name}'\t" + \
               f"Category: [{self.category}]" + \
               f"\nHighest price:{'': ^5}Price/unit: " + \
               f"{hi.price_per_unit_quantity}{'': ^4}{hi.name}" + \
               f"\nLowest price:{'': ^6}Price/unit: " + \
               f"{lo.price_per_unit_quantity}{'': ^4}{lo.name}" + \
               f"\nAverage price:{'': ^5}Price/unit: " + \
               f"{av:.2f}€/{lo.amount.unit}{'': ^4}\n"
