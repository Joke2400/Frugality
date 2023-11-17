from sqlalchemy.orm import Session

from app.core.orm import models, schemas


# STORE CRUD----------------------------------
def create_store(session: Session, store: schemas.StoreIn) -> models.Store:
    """Create a Store record."""
    db_store = models.Store(**dict(store))
    session.add(db_store)
    return db_store


def get_store(session: Session, store_id: int) -> models.Store | None:
    """Get a Store record by store id."""
    return session.query(models.Store).filter(
        models.Store.store_id == store_id).first()


def get_stores(session: Session) -> list[models.Store]:
    """Get all Stores in Stores table."""
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