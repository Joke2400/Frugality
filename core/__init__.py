"""Contains core app functionality."""
import asyncio
import configparser

from datetime import timedelta
from flask import Flask
from utils import LoggerManager
from utils import FrugalityPaths

from .store import Store
from .app import app as app_blueprint
from .orm import DataManager
from .orm import database

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# This segment will be moved into the (currently non-existent) 'process' file
# ----------------------------------------------------------------

# Temporary settings as it's not a priority
config = configparser.ConfigParser()
config.read(FrugalityPaths.settings_path())

with open(FrugalityPaths.secret_path(), "r", encoding="utf-8") as file:
    line = file.readline()
    if line == "":
        raise ValueError("Secret key cannot be an empty string.")
    SECRET_KEY = line

LIFETIME = timedelta(days=int(config["APP"]["lifetime"]))
TRACK_CHANGES = bool("True" in config["APP"]["track_changes"])
DB_PATH = FrugalityPaths.test_database_path()

logger = LoggerManager.get_logger(name=__name__)

flask_app = Flask(import_name="Frugality",
                  template_folder=FrugalityPaths.templates_path(),
                  static_folder=FrugalityPaths.static_path())
flask_app.register_blueprint(app_blueprint)

flask_app.secret_key = SECRET_KEY
flask_app.permanent_session_lifetime = LIFETIME
flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = TRACK_CHANGES

logger.debug("Set database uri to: 'sqlite:///%s'.", DB_PATH)
logger.debug("Set SQLALCHEMY_TRACK_MODIFICATIONS to: %s.", TRACK_CHANGES)
logger.debug("Set Flask session lifetime to: %s.", LIFETIME)

logger.debug("Initializing database...")
database.init_app(flask_app)
manager = DataManager(database=database, app=flask_app)

__all__ = ["Store"]
