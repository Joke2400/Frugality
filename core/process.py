from flask import Flask
from datetime import timedelta

class Process:
    
    def __init__(self, **kwargs):
        self.app = Flask("Frugality")
        self.app.secret_key = "TEMPORARY"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
        self.app.permanent_session_lifetime = timedelta(days=1)


    def start(self):
        self.app.run()