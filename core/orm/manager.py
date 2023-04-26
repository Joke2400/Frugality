from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from utils import LoggerManager

from .orm_classes import Store as StoreModel, Base as Model
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
            logger.exception(err.orig)
            logger.error(err.statement)
            self.db.session.rollback()
            return False
        return True

    def add_product_record(self, product: ProductItem) -> bool:
        self.
        
        
    def filtered_query(self, table: Model, key_value: dict):
        """Query a table and filter by a given field name and value."""
        if len(kwargs) > 1:
            raise ValueError("Length of key_value")
        logger.debug("Querying table '%s' with filter '%s'",
                     table, kwargs)
        return self.db.session.execute(
            self.db.select(table).filter_by(**kwargs)).scalars()
