from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from utils import LoggerManager

from .orm_classes import Store as StoreModel, Product as ProductModel, Base as Model
from ..store import Store
from ..product_classes import ProductItem


logger = LoggerManager.get_logger(name=__name__)


class DataManager:

    db: SQLAlchemy
    app: Flask
    _instance = None

    def __new__(cls):
        """
        Return singleton-instance stored in cls._instance.

        Create one if it doesn't already exist.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, database: SQLAlchemy, app: Flask):
        """Initialize instance with database and app."""
        self.db = database
        self.app = app

    def reset_db(self):
        """Drop all database tables and re-initialize them."""
        try:
            with self.app.app_context():
                self.db.drop_all()
                self.app.create_all()
        except SQLAlchemyError as err:
            logger.exception(err)

    def add_store_record(self, store: Store) -> bool:
        """
        Take in a core.store.Store and add it to database.

        Returns True if adding is successful, False if not.
        """
        record = StoreModel(
            store_id=store.store_id,
            name=store.name,
            slug=store.slug)
        logger.debug("Adding store (%s, %s, %s) to database.",
                     record.store_id, record.name, record.slug)
        self.db.session.add(record)
        try:
            self.db.session.commit()
        except IntegrityError as err:
            logger.exception(err)
            self.db.session.rollback()
            return False
        return True

    def add_product_record(self, product: ProductItem) -> bool:
        product = self.filter_query_all(ProductModel, {"store_id": product.store[1]})
        pass

    def filter_query_one(self, table: Model, key_value: dict):
        """Get one item in a table, filter results by the value provided."""
        if len(key_value) > 1:
            raise ValueError("More than one key was found in dict.")
        return self.db.session.execute(
            self.db.select(table).filter_by(**key_value)).scalar()

    def filter_query_all(self, table: Model, key_value: dict):
        """Get all items in a table, filter results by the value provided."""
        if len(key_value) > 1:
            raise ValueError("More than one key was found in dict.")
        return self.db.session.execute(
            self.db.select(table).filter_by(**key_value)).scalars()
