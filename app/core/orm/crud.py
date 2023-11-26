"""Contains CRUD operations for interaction with the database."""
from sqlalchemy.orm import Session

from app.core.orm import models, schemas, database


# STORE CRUD----------------------------------
def create_store(store: schemas.StoreBase) -> models.Store:
    """Create a Store record."""
    with database.DBContext() as session:
        db_store = models.Store(**dict(store))
        session.add(db_store)
        return db_store


def get_store_by_id(store: schemas.StoreQuery) -> models.Store | None:
    """Get a Store record by store id."""
    with database.DBContext() as session:
        return session.query(models.Store).filter(
            models.Store.store_id == store.store_id).first()


def get_stores_by_name(store: schemas.StoreQuery) -> list[models.Store] | None:
    """Get Store records by likeness to provided store name."""
    with database.DBContext() as session:
        return session.query(models.Store).filter(
            models.Store.store_name.like(store.store_name)).all()


def get_stores() -> list[models.Store]:
    """Get all Stores in Stores table."""
    with database.DBContext() as session:
        return session.query(models.Store).all()


# PRODUCT CRUD -------------------------------
def create_product(db: Session, product: schemas.ProductIn) -> None:
    pass


def get_product(db: Session):
    pass


# PRODUCT RECORD CRUD ------------------------
def create_product_record(db: Session, data: schemas.ProductRecordIn) -> None:
    pass


def get_product_record(db: Session):
    pass