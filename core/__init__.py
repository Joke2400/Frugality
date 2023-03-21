from utils import LoggerManager

logger = LoggerManager.get_logger(name=__name__, level=20, stream=True)

from .process import Process

process = Process()
app = process.app
db = process.db
