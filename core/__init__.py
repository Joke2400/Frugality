from .process import Process
from .app_dataclasses import QueryItem, ResultItem, AmountTuple, ProductList

process = Process()
app = process.app
db = process.db

from core.app import * #Change wildcard import later