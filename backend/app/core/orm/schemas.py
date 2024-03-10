"""Contains Pydantic schema definitions."""
from typing import TypeVar, Generic, Annotated
from datetime import datetime
from annotated_types import Len

import pydantic
from pydantic import Field

from backend.app.core.search_state import SearchState

StoreT = TypeVar("StoreT", bound="Store")
ProductT = TypeVar("ProductT", bound="Product")
ProductDataT = TypeVar("ProductDataT", bound="ProductDataDB")

# ---------------------------------------


class Store(pydantic.BaseModel):
    """Schema for stores going into DB/out of routes."""
    store_name: str
    store_id: int
    slug: str
    brand: str

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        frozen=True)


class StoreDB(Store, Generic[ProductT]):
    """Store schema equivalent to the orm model: 'Store'."""
    id: int
    timestamp: datetime
    products: list[ProductT] = pydantic.Field(
        default_factory=list)


# ---------------------------------------
class Product(pydantic.BaseModel):
    """Schema for products going into DB/out of routes."""
    name: str
    category: str
    ean: str
    slug: str
    brand: str

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        frozen=True)


class ProductDB(Product, Generic[ProductDataT]):
    """Product schema equivalent to the orm model: 'Product'."""
    id: int
    timestamp: datetime
    data: list[ProductDataT] = pydantic.Field(
        default_factory=list)


# ---------------------------------------


class ProductData(pydantic.BaseModel):
    """Schema for productdata going into DB/out of routes."""
    eur_unit_price_whole: int
    eur_unit_price_decimal: int
    eur_cmp_price_whole: int
    eur_cmp_price_decimal: int
    label_unit: str
    comparison_unit: str

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        frozen=True)


class ProductDataDB(ProductData):
    """Productdata schema equivalent to the orm model: 'ProductData'."""
    id: int
    timestamp: datetime

    store_id: int
    product_ean: int
    store: Store
    product: Product


# ---------------------------------------


class ProductQuery(pydantic.BaseModel):
    """Schema for how queries for products should look like"""
    stores: Annotated[set[int], Len(min_length=0, max_length=10)]
    queries: Annotated[list[dict[str, str]], Len(min_length=0, max_length=30)]

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "stores": [
                        542862479,
                        697942431

                    ],
                    "queries": [
                        {"query": "Maito Laktoositon 1L",
                         "category": ""},
                        {"query": "Naudan Jauheliha",
                         "category": ""},
                        {"query": "Peruna",
                         "category": ""}
                    ]
                }
            ]
        })


class StoreQuery(pydantic.BaseModel):
    """Schema for how queries for stores should look like"""
    store_name: Annotated[str | None, Len(min_length=1, max_length=50)]
    store_id: int | None = Field(ge=0, le=999999999)

    model_config = pydantic.ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "store_name": "Prisma Olari",
                    "store_id": 542862479
                }
            ]
        })

    @pydantic.model_validator(mode="after")
    def check_either_provided(self):
        """Check that either a name or id was provided to the model."""
        if self.store_name is None and self.store_id is None:
            raise ValueError("Either a name or id is required.")
        return self

    def __str__(self) -> str:
        return f"<store_name='{self.store_name}', store_id={self.store_id}>"


class ProductResponse(pydantic.BaseModel):
    """Schema format for the response to a product query."""
    results: dict[
        int,
        list[
            tuple[
                SearchState,
                dict[str, str | int],  # Contains original query info
                list[
                    tuple[
                        Product,
                        ProductData
                    ]
                ]
            ]
        ]
    ]

    @pydantic.computed_field
    def unique_queries(self) -> int:
        """Get the unique query count in the response."""
        try:
            return len(next(iter(self.results.values())))
        except IndexError:
            return 0

    @pydantic.computed_field
    def total_queries(self) -> int:
        """Get the total query count in the response."""
        return self.unique_queries * len(self.results)  # type: ignore

    def __str__(self) -> str:
        return f"ProductResponse<total_queries={self.total_queries}>"


class StoreResponse(pydantic.BaseModel):
    """Schema format for the response to a store query."""
    results: list[Store]

    def __str__(self) -> str:
        return f"StoreResponse<length={len(self.results)} stores>"
