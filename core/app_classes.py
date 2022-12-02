from utils import LoggerManager as lgm
from dataclasses import dataclass, field
from requests import Response
import core

logger = lgm.get_logger(name=__name__)


@dataclass
class AmountData:
    quantity: int | None
    unit: str | None
    multiplier: int = 1
    quantity_str: str = ""

    def __repr__(self) -> str:
        return "AmountData(" +\
               f"quantity={self.quantity} " +\
               f"unit={self.unit} " +\
               f"multiplier={self.multiplier} " +\
               f"quantity_str='{self.quantity_str}')"

    def __str__(self) -> str:
        return f"{self.multiplier} x {self.quantity_str}"


@dataclass
class PriceData:
    unit_price: int | float  # Basic price
    cmp_price: int | float   # Comparison price (value for price per unit)

    def __repr__(self) -> str:
        return "PriceData(" +\
               f"unit_price={self.unit_price} " +\
               f"cmp_price={self.cmp_price})"

    def __str__(self) -> str:
        return f"Price: {self.unit_price} " + \
               f"Comparison Price: {self.cmp_price}"


@dataclass
class QueryItem:
    name: str
    store: tuple[str | None, int | None]
    category: str | None
    amount: AmountData

    def __repr__(self) -> str:
        return "QueryItem(" +\
               f"name={self.name} " +\
               f"amount={repr(self.amount)} " + \
               f"category={self.category})"

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
    def quantity(self) -> str:
        return self.amount.quantity_str

    @property
    def unit(self) -> str | None:
        return self.amount.unit

    @property
    def total_price(self) -> float:
        return float(self.amount.multiplier * self.price.unit_price)

    @property
    def total_price_str(self) -> str:
        price = self.amount.multiplier * self.price.unit_price
        return f"{self.amount.multiplier}x for " + \
               f"{price:.2f}€"

    @property
    def price_per_item(self) -> float:
        return float(self.price.unit_price)

    @property
    def price_per_unit(self) -> float:
        return float(self.price.cmp_price)

    @property
    def price_per_unit_str(self) -> str:
        return f"{self.price_per_item:.2f}€ for {self.quantity}"

    @property
    def price_per_unit_quantity_str(self) -> str:
        return f"{self.price_per_unit:.2f}€/{self.unit}"

    def __repr__(self) -> str:
        return "ProductItem(" +\
               f"name={self.name} " +\
               f"amount={self.amount} " +\
               f"category={self.category} " +\
               f"ean={self.ean} " + \
               f"price={self.price})"

    def __str__(self) -> str:
        return f"\n[Name]: '{self.name}'\n" \
               f"[EAN]: {self.ean}\n" + \
               f"[Quantity]: {self.amount}\n" + \
               f"[Price]: {self.price_per_item}\n" + \
               f"[Price/unit]: {self.price_per_unit_quantity_str}\n" + \
               f"[Total price]: {self.total_price}\n"


@dataclass
class ProductList:
    response: Response
    query: QueryItem
    _items: list[ProductItem] = field(default_factory=list)

    def __post_init__(self):
        self.store = self.query.store
        self.category = self.query.category
        self._filter = None
        self._fitems = []

    def parse(self) -> None:
        self._items = []
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

            self._items.append(item)
        logger.debug(f"Parsed {len(self._items)} items from response")

    @property
    def products(self) -> list[ProductItem]:
        logger.debug("Property 'ProductList.products' was called.")
        if len(self._items) == 0:
            logger.debug("Product list empty, parsing response...")
            self.parse()
        if self._filter is None:
            logger.debug("Filter not applied, returning all products...")
            items = self._items
        if isinstance(self._filter, str):
            logger.debug("Returning filtered products...")
            if len(self._fitems) == 0:
                self._fitems = self._get_filtered_products(
                    self._items, self._filter)
            items = self._fitems
        else:
            items = self._items
        return items

    @staticmethod
    def _get_filtered_products(p: list[ProductItem], f: str
                               ) -> list[ProductItem]:
        if len(p) == 0:
            logger.debug("Cannot filter products, no products to filter.")
            return p
        logger.debug(f"Original len(): {len(p)}")
        logger.debug(f"Filter string: '{f}'")
        items = p
        if f is not None or f != "":
            items = []
            for i in filter(lambda p: str(p.amount.quantity) == f, p):
                items.append(i)
            logger.debug(f"Filtered len(): {len(items)}")
        else:
            logger.debug("Filter empty, returning unfiltered product list.")
        return items

    def set_filter(self, filter_str: str | int | float) -> None:
        try:
            self._filter = str(filter_str)
            logger.debug(f"Set filter to: '{self._filter}'.")
        except ValueError:
            logger.debug("Could not set filter.")

    def reset_filter(self) -> None:
        self._filter = None
        logger.debug("Reset filter to: 'None'.")

    @property
    def highest_priced_cmp(self) -> ProductItem | None:
        p = self.products
        if len(p) == 0:
            return None
        i = max(p, key=lambda x: x.price_per_unit)
        logger.debug(f"Highest priced item: {i.price_per_unit} {i.name}")
        return i

    @property
    def lowest_priced_cmp(self) -> ProductItem | None:
        p = self.products
        if len(p) == 0:
            return None
        i = min(p, key=lambda x: x.price_per_unit)
        logger.debug(f"Lowest priced item: {i.price_per_unit} {i.name}")
        return i

    @property
    def average_priced_cmp(self) -> ProductItem | None:
        p = self.products
        if len(p) == 0:
            return None
        i = sum(i.price_per_unit for i in p) / len(p)
        c = p[0]
        for x in p[1:]:
            comparison = x.price_per_unit
            closest = c.price_per_unit
            if abs(comparison - i) < abs(closest - i):
                c = x
        logger.debug(f"Average priced item: {c.price_per_unit} {c.name}")
        return c

    def get_overview_str(self):
        # Considering this is a print function, it's quite expensive
        # However the thinking is that this shouldn't be called in
        # practice because this responsibility should fall on the client side
        # Client side could also have the responsibility of calculating
        # max min and avg on it's own

        # min/max/avg results are dependent on whether
        # or not a filter string has been set by set_filter
        hi = self.highest_priced_cmp
        lo = self.lowest_priced_cmp
        av = self.average_priced_cmp

        # Shortening the needed variable names so
        # that the strings below are easier to read
        n = self.query.name
        s = self.store
        c = self.category

        h = (hi.total_price_str,
             hi.price_per_unit_str,
             hi.price_per_unit_quantity_str)

        l = (lo.total_price_str,
             lo.price_per_unit_str,
             lo.price_per_unit_quantity_str)

        a = (av.total_price_str,
             av.price_per_unit_str,
             av.price_per_unit_quantity_str)

        d_str = f"Query: '{n}' Store: '{s[0]}' ID: '{s[1]}' Category: '{c}'\n"

        h_str = f"\nHighest price:{'': ^5}Total price: {h[0]} " + \
                f"{'': ^2}Price: {h[1]}{'': ^3}Price/unit: {h[2]} {hi.name}"

        l_str = f"\nLowest price:{'': ^6}Total price: {l[0]} " + \
                f"{'': ^2}Price: {l[1]}{'': ^3}Price/unit: {l[2]} {lo.name}"

        a_str = f"\nAverage price:{'': ^5}Total price: {a[0]} " + \
                f"{'': ^2}Price: {a[1]}{'': ^3}Price/unit: {a[2]} {av.name}\n"

        s = d_str + h_str + l_str + a_str
        return s

    def __str__(self) -> str:
        s = self.get_overview_str()
        return s
