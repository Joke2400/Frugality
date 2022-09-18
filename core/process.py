from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask import Flask
from utils import Paths

import asyncio


class Process:

    def __init__(self):
        self.app = Flask("Frugality", template_folder=Paths.templates(),
                         static_folder=Paths.static())
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.app.secret_key = "TEMPORARY"
        self.db_path = Paths.test_database()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = \
            f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        self.app.permanent_session_lifetime = timedelta(days=1)
        self.db = SQLAlchemy(self.app)

    def start(self, debug=False, reset=False):
        from core.database_manager import DataManager
        # Avoiding a circular import :)
        self.data_manager = DataManager(db=self.db)
        self.data_manager.start_db(reset=reset)
        self.app.run(debug=debug)
