"""Models definitions for the SQLAlchemy ORM."""
from typing import List, Callable
from datetime import datetime

from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.types import DateTime, ARRAY, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from . import database
Base = database.Base


func: Callable  # type: ignore | False positive in sqlalchemy

# TODO: Better documentation over relationships etc


class Store(Base):
    """An SQLAlchemy ORM mapping for a store item."""
    __tablename__ = "Stores"

    # Unique identifiers
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(unique=True)
    store_name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)

    brand: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    # One-To-Many relationship
    products: Mapped[List["ProductData"]] = relationship(
        back_populates="store")


class Product(Base):
    """An SQLAlchemy ORM mapping for a product item."""
    __tablename__ = "Products"

    # Unique identifiers
    id: Mapped[int] = mapped_column(primary_key=True)
    ean: Mapped[str] = mapped_column(unique=True)

    # Some products may have the same names but different EANs
    name: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column()
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String))
    category: Mapped[str] = mapped_column()
    brand: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    # One-To-Many relationship
    data: Mapped[List["ProductData"]] = relationship(
        back_populates="product",
        cascade="save-update, merge, delete, delete-orphan",
        passive_deletes=True)


class ProductData(Base):
    """An SQLAlchemy ORM mapping for a product data item."""
    __tablename__ = "ProductData"

    # Unique identifiers
    id: Mapped[int] = mapped_column(primary_key=True)

    eur_unit_price_whole: Mapped[int] = mapped_column()
    eur_unit_price_decimal: Mapped[int] = mapped_column()
    eur_cmp_price_whole: Mapped[int] = mapped_column()
    eur_cmp_price_decimal: Mapped[int] = mapped_column()
    label_unit: Mapped[str] = mapped_column()
    comparison_unit: Mapped[str] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    # Foreign keys for parent store id & parent product id
    store_id: Mapped[int] = mapped_column(ForeignKey("Stores.store_id"))
    product_ean: Mapped[int] = mapped_column(ForeignKey(
        "Products.ean", ondelete="CASCADE"))

    # Reverse sides (Many-to-One) of the One-To-Many relationships
    store: Mapped["Store"] = relationship(back_populates="products")
    product: Mapped["Product"] = relationship(back_populates="data")
