from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapped_column, Mapped

db = SQLAlchemy()
Base = db.Model


class Product(Base):

    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(primary_key=True)
    ean: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
