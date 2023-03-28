from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()
Base = db.Model

class Store(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str] = mapped_column(unique=True)


class Product(Base):

    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ean: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
