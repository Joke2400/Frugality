from .skaupat_queries import queries as s_queries
from utils import LoggerManager as lgm
from .skaupat_api import (
    api_fetch_products,
    api_get_store
)

logger = lgm.get_logger(name=__name__, level=20, stream=True)
