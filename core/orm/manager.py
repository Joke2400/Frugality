from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from utils import LoggerManager

from .orm_classes import Store, Base as Model
from ..store_class import Store as StoreDataclass


logger = LoggerManager.get_logger(name=__name__)


class DataManager:

    db: SQLAlchemy
    app: Flask
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def set_configuration(cls, database: SQLAlchemy, app: Flask):
        logger.debug("Setting database configuration...")
        cls.db = database
        cls.app = app

    @classmethod
    def initialize_db_tables(cls):
        with cls.app.app_context():
            cls.db.create_all()
        logger.debug("Initialized database tables.")

    @classmethod
    def filtered_query(cls, table: Model, **kwargs):
        if len(kwargs) > 1:
            # Get first key-value pair in kwargs
            items = next(iter(kwargs.items()))
            kwargs = {items[0]: items[1]}
        logger.debug("Querying table '%s' with filter '%s'",
                     table, kwargs)
        return cls.db.session.execute(
            cls.db.select(table).filter_by(**kwargs)).scalars()

    @classmethod
    def add_store_record(cls, store: StoreDataclass) -> None:
        try:
            db_store = Store(
                store_id=store.store_id,
                name=store.name,
                slug=store.slug)
            logger.debug(
                "Attempting to add store '%s', '%s' to db",
                db_store.store_id, db_store.name)
            cls.db.session.add(store)
            cls.db.session.commit()
            logger.debug("Commit successful!")
        except Exception as err:  # Temporary
            logger.exception("Commit Failed! %s", err)
