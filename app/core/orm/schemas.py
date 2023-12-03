"""Contains Pydantic schema definitions."""
from typing import TypeVar, Generic
from datetime import datetime

import pydantic


StoreT = TypeVar("StoreT", bound=pydantic.BaseModel)
ProductT = TypeVar("ProductT", bound=pydantic.BaseModel)
ProductRecordT = TypeVar("ProductRecordT", bound=pydantic.BaseModel)


class StoreBase(pydantic.BaseModel):
    store_name: str


class Store(StoreBase):
    store_id: int
    slug: str
    brand: str

    model_config = pydantic.ConfigDict(from_attributes=True)


class StoreDB(Store, Generic[ProductT]):
    id: int
    timestamp: datetime
    products: list[ProductT] = pydantic.Field(default_factory=list)


"""
class ProductIn(pydantic.BaseModel):

    ean: str
    name: str
    slug: str
    category: str
    brand: str


class ProductOut(ProductIn, Generic[ProductRecordT]):

    id: int
    timestamp: datetime
    aliases: list[str] = []
    data: list[ProductRecordT] = []

    class Config:

        from_attributes = True


class ProductRecordIn(pydantic.BaseModel):

    eur_unit_price_whole: int
    eur_unit_price_decimal: int
    eur_cmp_price_whole: int
    eur_cmp_price_decimal: int
    label_unit: str
    comparison_unit: str


class ProductRecordOut(ProductRecordIn, Generic[StoreT, ProductT]):

    id: int
    timestamp: datetime

    store_id: int
    product_id: int

    store: StoreT
    product: ProductT

    class Config:

        from_attributes = True
"""