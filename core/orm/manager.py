from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from utils import LoggerManager
from utils import SingletonMeta

from .orm_classes import Base as Model
from .orm_classes import Store as StoreModel
from .orm_classes import ProductBase as ProductBaseModel
from .orm_classes import ProductData as ProductDataModel
from ..product import Product as ProductItem
from ..store import Store as StoreItem


logger = LoggerManager.get_logger(name=__name__)


class DataManager(metaclass=SingletonMeta):

    database: SQLAlchemy
    app: Flask
    _instance = None

    def __init__(self, **kwargs):
        """Initialize manager with database and app.

        __init__ needs to be provided two fields:
        database: flask_sqlalchemy.SQLAlchemy
        app: flask.Flask
        """
        self.database = kwargs.get("database", None)
        self.app = kwargs.get("app", None)
        self.path = kwargs.get("path", None)
        if self.database is None or self.app is None:
            raise TypeError(
                ".__init__() needs a 'database' and 'app' as params.")
        if self.path is not None:
            if not self.path.exists():
                self.reset_db()

    def filter_query(self, table: Model, key_value: dict):
        """Fetch items from a table, filter results by the value provided."""
        if len(key_value) > 1:
            raise ValueError("More than one key was found in dict.")
        result = self.database.session.scalars(
            self.database.select(table).filter_by(**key_value))
        return result

    def add_store(self, store: StoreItem) -> tuple[bool]:
        """
        Take in a core.store.Store and add it to database.

        Returns True if adding is successful, False if not.
        """
        logger.debug("Adding %s to database.", store)
        item = StoreModel(
            store_id=store.store_id,
            name=store.name,
            slug=store.slug)
        return self.add_and_commit(item)

    def add_product_base(self, product: ProductItem) -> tuple[bool, Model]:
        logger.debug("Adding product identifiers (%s %s %s) to database.",
                     product.ean, product.name, product.category)
        item = ProductBaseModel(
            ean=product.ean,
            name=product.name,
            category=product.category)
        return self.add_and_commit(item), item

    def add_product_data(self, product: ProductItem, store) -> tuple[bool]:
        try:
            product_base = self.filter_query(
                ProductBaseModel, {"ean": product.ean}).one()
        except NoResultFound:
            result, product_base = self.add_product_base(product)
            if not result:
                logger.debug("TEMP: Could not add ProductBaseModel")
                return False
        product_data = ProductDataModel(
            cmp_price_int=1,
            cmp_price_decimal=11,
            unit_price_int=2,
            unit_price_decimal=22
        )
        product_data.store = store
        product_data.product = product_base

        self.add_and_commit(product_data)
        print("DONE!")

    def add_and_commit(self, item: Model):
        """Add and commit a Model to database.

        If an IntegrityError is raised, rolls back the transaction.
        """
        self.database.session.add(item)
        try:
            self.database.session.commit()
        except IntegrityError:
            self.database.session.rollback()
            return False
        return True

    def reset_db(self):
        """Drop all database tables and re-initialize them."""
        try:
            with self.app.app_context():
                self.database.drop_all()
                self.database.create_all()
        except SQLAlchemyError as err:
            logger.exception(err)
