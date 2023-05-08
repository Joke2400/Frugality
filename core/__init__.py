"""Contains core app functionality."""

import asyncio
from datetime import timedelta
from flask import Flask
from utils import LoggerManager
from utils import ProjectPaths
from .app import app as app_blueprint
from .orm import DataManager
from .orm import database

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# This segment will be moved into the (currently non-existent) 'Process' class
# ----------------------------------------------------------------

# Temporary settings as it's not a priority
SECRET_KEY = "TEMPORARY"
LIFETIME = timedelta(days=1)
DB_PATH = ProjectPaths.test_database()
KEEP_TRACK = True

logger = LoggerManager.get_logger(name=__name__)

flask_app = Flask(import_name="Frugality",
                  template_folder=ProjectPaths.templates(),
                  static_folder=ProjectPaths.static())
flask_app.register_blueprint(app_blueprint)

flask_app.secret_key = SECRET_KEY
flask_app.permanent_session_lifetime = LIFETIME
flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = KEEP_TRACK

logger.debug("Set database uri to: 'sqlite:///%s'.", DB_PATH)
logger.debug("Set SQLALCHEMY_TRACK_MODIFICATIONS to: %s.", KEEP_TRACK)
logger.debug("Set Flask session lifetime to: %s.", LIFETIME)

logger.debug("Initializing database...")
database.init_app(flask_app)
manager = DataManager(database=database, app=flask_app)
manager.reset_db()

"""
from .orm.orm_classes import Store as db_Store
from .store import Store
from .product_classes import ProductItem
from utils import Found
store = Store("Prisma Olari", 542862479, "prisma-olari", Found())
with flask_app.app_context():
    result = manager.add_store(store)
    store = manager.filter_query(db_Store, {"store_id": 542862479}).one()
    
    product = ProductItem(
        name="Test Item",
        count=2,
        category="test-category-string",
        ean="0618429381242",
        store=("Prisma Olari", "542862479", "prisma-olari"),
        comparison_unit="dl",
        comparison_price=1.59,
        unit_price=6.2)
    manager.add_product_data(product, store)
    store = manager.filter_query(db_Store, {"store_id": 542862479}).one()
    print(store.products)
    print(store.products[0].cmp_price_int)
"""