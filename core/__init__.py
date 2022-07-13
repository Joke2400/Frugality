
from flask_sqlalchemy import SQLAlchemy

from .process import Process
from utils import Paths

process = Process()



db_path = Paths.database()
app = Flask(__name__)
app.secret_key = "test"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.permanent_session_lifetime = timedelta(days=1)

from core.app import *

