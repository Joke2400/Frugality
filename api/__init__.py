from .skaupat_queries import queries as s_queries
from utils import LoggerManager as lgm
from .skaupat_api import (
    get_groceries
)

logger = lgm.get_logger(name=__name__, level=30, stream=True)
