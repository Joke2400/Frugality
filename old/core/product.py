"""Contains a product dataclass for storing query results."""

from dataclasses import dataclass
from utils import LoggerManager

from .store import Store


logger = LoggerManager.get_logger(name=__name__)


@dataclass(frozen=True, slots=True)
class PriceData:
    """Dataclass that represents price data."""

    price: float
    basic_quantity_unit: str

    comparison_price: float
    comparison_unit: str

    @property
    def data(self) -> tuple[float, str, float, str]:
        """Get price fields as a tuple."""
        return (self.price, self.basic_quantity_unit,
                self.comparison_price, self.comparison_unit)


@dataclass(frozen=True, slots=True)
class Product:
    """Dataclass that represents a product."""

    ean: str   # Unique
    slug: str  # Unique
    name: str  # Unique
    brand_name: str
    category: str
    category_str_path: str

    store: Store
    price_data: PriceData

    def get_total_price(self, count: int) -> float:
        """Return total price of the product."""
        return self.price_data.price * count

    def dictify(self) -> dict:
        """Convert data to a dict and return it.

        Store field is omitted as it's redundant in the final dict.
        """
        return {
            "ean": self.ean,
            "slug": self.slug,
            "name": self.name,
            "brand_name": self.brand_name,
            "category": self.category,
            "category_str_path": self.category_str_path,
            "price_data": self.price_data.data
        }

    def __repr__(self) -> str:
        """Return name and price of item."""
        return f"<{self.name} {self.price_data.price}€>"
