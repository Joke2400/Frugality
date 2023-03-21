from utils import LoggerManager

logger = LoggerManager.get_logger(name=__name__, level=20, stream=True)

from .process import Process

process = Process()
flask_app = process.app
db = process.db

from .app import *  # These damn imports are awful and need to be reworked