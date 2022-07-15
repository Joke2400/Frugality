from flask import Flask
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy

from utils import Paths
from .database_manager import data_manager

class Process:
    
    def __init__(self, **kwargs):
        self.app = Flask("Frugality", template_folder=Paths.templates())
        self.app.secret_key = "TEMPORARY"
        self.db_path = Paths.test_database()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        self.app.permanent_session_lifetime = timedelta(days=1)
        self.db = SQLAlchemy(self.app)
        self.data_manager = data_manager(self.db)

    def start(self):
        self.data_manager.start_db()
        self.app.run() 