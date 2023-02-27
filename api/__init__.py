from .skaupat_queries import queries as s_queries
from utils import LoggerManager as lgm

logger = lgm.get_logger(name=__name__, stream=True)

from .skaupat_api import (
    api_fetch_products,
    api_fetch_store
)