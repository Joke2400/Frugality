from utils import LoggerManager as lgm
from dataclasses import dataclass, field
from requests import Response
import core

logger = lgm.get_logger(name=__name__)


@dataclass
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
    store: tuple[str, int] | None = None
    unit_price: int | float | None = None
    comparison_price: int | float | None = None

    # User-defined data
    multiplier: int = 1

    @property
    def quantity_string(self) -> str:
        return f"{self.quantity}/{self.unit}"

    @property
    def total_price(self) -> int | float:
        return self.multiplier * self.unit_price


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
