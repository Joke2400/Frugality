"""Contains Pydantic schema definitions."""
from typing import TypeVar
from typing import Generic
from datetime import datetime
from pydantic import BaseModel


StoreT = TypeVar("StoreT", bound="StoreOut")
ProductT = TypeVar("ProductT", bound="ProductOut")
ProductRecordT = TypeVar("ProductRecordT", bound="ProductRecordOut")


class StoreIn(BaseModel):
    """Pydantic model for a store going into the database."""
    store_id: str
    name: str
    slug: str
    brand: str


class StoreOut(StoreIn, Generic[ProductT]):
    """Pydantic model for a store coming out of the database."""

    id: int
    timestamp: datetime
    products: list[ProductT] = []

    class Config:
        """Pydantic config."""
        from_attributes = True


class ProductIn(BaseModel):
    """Pydantic model for a product going into the database."""
    ean: str
    name: str
    slug: str
    category: str
    brand: str


class ProductOut(ProductIn, Generic[ProductRecordT]):
    """Pydantic model for a product coming out of the database."""
    id: int
    timestamp: datetime
    aliases: list[str] = []
    data: list[ProductRecordT] = []

    class Config:
        """Pydantic config."""
        from_attributes = True


class ProductRecordIn(BaseModel):
    """Pydantic model for a product record going into the database."""
    eur_unit_price_whole: int
    eur_unit_price_decimal: int
    eur_cmp_price_whole: int
    eur_cmp_price_decimal: int
    label_unit: str
    comparison_unit: str


class ProductRecordOut(ProductRecordIn, Generic[StoreT, ProductT]):
    """Pydantic model for a product record coming out of the database."""
    id: int
    timestamp: datetime

    store_id: int
    product_id: int

    store: StoreT
    product: ProductT

    class Config:
        """Pydantic config."""
        from_attributes = True
