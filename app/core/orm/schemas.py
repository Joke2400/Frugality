"""Contains Pydantic schema definitions."""
from typing import TypeVar, Generic
from datetime import datetime

import pydantic


StoreT = TypeVar("StoreT", bound="Store")
ProductT = TypeVar("ProductT", bound="Product")
ProductDataT = TypeVar("ProductDataT", bound="ProductDataDB")

# ---------------------------------------


class StoreBase(pydantic.BaseModel):
    """Store base schema."""
    store_name: str


class Store(pydantic.BaseModel):
    """Store schema for items going in/out of routes."""
    store_name: str
    store_id: int
    slug: str
    brand: str

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "store_name": "Prisma Olari",
                    "store_id": 542862479,
                    "slug": "prisma-olari",
                    "brand": "prisma"
                }
            ]
        })


class StoreDB(Store, Generic[ProductT]):
    """Complete schema for a Store, equivalent to DB Store model."""
    id: int
    timestamp: datetime
    products: list[ProductT] = pydantic.Field(
        default_factory=list)


# ---------------------------------------


class ProductBase(pydantic.BaseModel):
    "Product base schema."
    name: str
    category: str


class Product(ProductBase):
    """Store schema for items going in/out of routes."""
    ean: str
    slug: str
    brand: str
    aliases: list[str] = pydantic.Field(
        default_factory=list)

    model_config = pydantic.ConfigDict(
        from_attributes=True)


class ProductDB(Product, Generic[ProductDataT]):
    """Complete schema for a Product, equivalent to DB Product model."""
    id: int
    timestamp: datetime
    data: list[ProductDataT] = pydantic.Field(
        default_factory=list)


# ---------------------------------------


class ProductData(pydantic.BaseModel):
    """ProductData schema."""
    eur_unit_price_whole: int
    eur_unit_price_decimal: int
    eur_cmp_price_whole: int
    eur_cmp_price_decimal: int
    label_unit: str
    comparison_unit: str

    model_config = pydantic.ConfigDict(
        from_attributes=True)


class ProductDataDB(ProductData):
    """Complete schema for ProductData, equivalent to DB ProductData Model"""
    id: int
    timestamp: datetime

    store_id: int
    product_id: int
    store: Store
    product: Product


# ---------------------------------------


class ProductQuery(pydantic.BaseModel):
    """Schema for how product searches should look like."""
    stores: set[int]
    queries: list[dict[str, str]]

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "stores": [
                        542862479,
                        647396324
                    ],
                    "queries": [
                        {"query": "Maito Laktoositon 1L",
                         "category": "Maito, munat ja rasvat"},
                        {"query": "Naudan Jauheliha 400g",
                         "category": ""},
                        {"query": "Leipä",
                         "category": ""}
                    ]
                }
            ]
        })
