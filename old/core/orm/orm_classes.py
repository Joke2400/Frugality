import datetime
from typing import List

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
from sqlalchemy.types import DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped


database = SQLAlchemy()
Base = database.Model


class Store(Base):

    __tablename__ = "Stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column(unique=True)

    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    products: Mapped[List["ProductData"]] = relationship(
        back_populates="store")


class ProductBase(Base):

    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ean: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    brand_name: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    category_str_path: Mapped[str] = mapped_column()

    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    data: Mapped[List["ProductData"]] = relationship(
        back_populates="product")


class ProductData(Base):

    __tablename__ = "ProductData"

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float] = mapped_column()
    basic_quantity_unit: Mapped[str] = mapped_column()
    comparison_price: Mapped[float] = mapped_column()
    comparison_unit: Mapped[str] = mapped_column()

    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    store_id: Mapped[int] = mapped_column(ForeignKey("Stores.id"))
    store: Mapped["Store"] = relationship(back_populates="products")
    product_id: Mapped[int] = mapped_column(ForeignKey("Products.id"))
    product: Mapped["ProductBase"] = relationship(back_populates="data")
