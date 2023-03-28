from flask_sqlalchemy import SQLAlchemy
from flask import Flask

from .orm_classes import Product


class DataManager:

    __instance = None
    database: SQLAlchemy | None = None
    app: Flask | None = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def set_configuration(cls, database: SQLAlchemy, app: Flask):
        cls.database = database
        cls.app = app

    @classmethod
    def initialize_db_tables(cls):
        with cls.app.app_context():
            cls.database.create_all()
