"""Contains core app functionality."""

import asyncio
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from utils import LoggerManager
from utils import ProjectPaths
from .app import app as app_blueprint

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
logger = LoggerManager.get_logger(name=__name__)

flask_app = Flask(import_name="Frugality",
                  template_folder=ProjectPaths.templates(),
                  static_folder=ProjectPaths.static())
flask_app.register_blueprint(app_blueprint)

# Temporary settings as it's not a priority
SECRET_KEY = "TEMPORARY"
LIFETIME = timedelta(days=1)
DB_PATH = ProjectPaths.test_database()
KEEP_TRACK = True

flask_app.secret_key = SECRET_KEY
flask_app.permanent_session_lifetime = LIFETIME
flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = KEEP_TRACK

logger.debug("Set database uri to: 'sqlite:///%s'.", DB_PATH)
logger.debug("Set SQLALCHEMY_TRACK_MODIFICATIONS to: %s.", KEEP_TRACK)
logger.debug("Set Flask session lifetime to: %s.", LIFETIME)

flask_db = SQLAlchemy(flask_app)
