from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import List

db = SQLAlchemy()
Base = db.Model


class Store(Base):

    __tablename__ = "Stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)
    products: Mapped[List["StoreProductData"]] = relationship(
        back_populates="store")


class Product(Base):

    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ean: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[str] = mapped_column()
    data: Mapped[List["StoreProductData"]] = relationship(
        back_populates="product")


class StoreProductData(Base):

    __tablename__ = "ProductData"

    id: Mapped[int] = mapped_column(primary_key=True)

    store_id: Mapped[int] = mapped_column(ForeignKey("Stores.id"))
    store: Mapped["Store"] = relationship(back_populates="products")

    product_id: Mapped[int] = mapped_column(ForeignKey("Products.id"))
    product: Mapped["Product"] = relationship(back_populates="data")

    cmp_price_int: Mapped[int] = mapped_column()
    cmp_price_decimal: Mapped[int] = mapped_column()
    unit_price_int: Mapped[int] = mapped_column()
    unit_price_decimal: Mapped[int] = mapped_column()
