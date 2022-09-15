from flask import Flask
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy

from utils import Paths

class Process:
    
    def __init__(self):
        self.app = Flask("Frugality", template_folder=Paths.templates(), static_folder=Paths.static())
        self.app.secret_key = "TEMPORARY"
        self.db_path = Paths.test_database()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{self.db_path}"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        self.app.permanent_session_lifetime = timedelta(days=1)
        self.db = SQLAlchemy(self.app)

    def start(self, debug=False, reset=False):
        from .database_manager import data_manager
        #Breaking convention to avoid a circular import :)
        #Otherwise sqlalchemy_db_classes would need to be in same file as data_manager
        self.data_manager = data_manager
        self.data_manager.start_db(reset=reset)
        self.app.run(debug=debug) 