from .process import Process

process = Process()
app = process.app
db = process.db

from core.app import * #Change wildcard import later