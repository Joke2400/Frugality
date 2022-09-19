from flask_sqlalchemy import SQLAlchemy
from utils import configure_logger
from datetime import timedelta
from flask import Flask
from utils import Paths

import asyncio

TEST_MODE = True
TRACK = True
LIFETIME = timedelta(days=1)
logger = configure_logger(name=__name__, level=20 if not TEST_MODE else 10,
                          log_to_stream=True, log_to_file=True)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Process:

    def __init__(self):
        self.app = Flask(import_name="Frugality",
                         template_folder=Paths.templates(),
                         static_folder=Paths.static())
        self.app.secret_key = "TEMPORARY"
        if TEST_MODE:
            self.db_path = Paths.test_database()
        else:
            self.db_path = Paths.database()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = \
            f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = TRACK
        self.app.permanent_session_lifetime = LIFETIME

        logger.info(f"Set database uri to: 'sqlite:///{self.db_path}'.")
        logger.debug(f"Set SQLALCHEMY_TRACK_MODIFICATIONS to: {TRACK}.")
        logger.debug(f"Set Flask session lifetime to: {LIFETIME}.")

        self.db = SQLAlchemy(self.app)

    def start(self, debug=False, reset=False):
        from core.database_manager import DataManager
        # Avoiding a circular import :)
        self.data_manager = DataManager(db=self.db)
        self.data_manager.start_db(reset=reset)
        self.app.run(debug=debug)
