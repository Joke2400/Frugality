from sqlalchemy.orm import Session

from app.core.orm import models, schemas, DBContext


# STORE CRUD----------------------------------
def create_store(store: schemas.StoreIn) -> None:
    """Create a Store record."""
    db_store = models.Store(**dict(store))
    with DBContext() as session:
        session.add(db_store)


def get_store(store_id: int):
    """Get a Store record by store id."""
    with DBContext() as session:
        return session.query(models.Store).filter(
            models.Store.store_id == store_id).first()


def get_stores():
    """Get all Stores in Stores table."""
    with DBContext() as session:
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