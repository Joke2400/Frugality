"""Contains Pydantic schema definitions."""
from typing import TypeVar, Generic
from datetime import datetime

import pydantic
from app.utils import exceptions


StoreT = TypeVar("StoreT", bound=pydantic.BaseModel)
ProductT = TypeVar("ProductT", bound=pydantic.BaseModel)
ProductRecordT = TypeVar("ProductRecordT", bound=pydantic.BaseModel)


class StoreBase(pydantic.BaseModel):
    """"Schema for a Store going into the database."""

    store_name: str
    store_id: str
    slug: str
    brand: str

    class Config:
        """Pydantic config."""
        from_attributes = True


class StoreDB(StoreBase, Generic[ProductT]):
    """"Schema for a Store coming out of the database."""
    id: int
    timestamp: datetime
    products: list[ProductT] = []


class StoreQuery(pydantic.BaseModel):
    """Schema for a user query for a store."""
    store_name: str | None = None
    store_id: str | None = None
    brand: str | None = None

    class Config:
        """Pydantic config."""
        from_attributes = True

    # TODO: Figure out a working model validator that doesn't make my life harder


class ProductIn(pydantic.BaseModel):
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


class ProductRecordIn(pydantic.BaseModel):
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
