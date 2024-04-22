from backend.app.utils.util_funcs import get_envvar
from backend.app.core.orm.database import ORM

postgres_user = get_envvar("POSTGRES_USER")
postgres_password = get_envvar("POSTGRES_PASSWORD")
postgres_port = get_envvar("POSTGRES_PORT")

auth = f"{postgres_user}:{postgres_password}"
host = f"localhost:{postgres_port}/test_database"
url = f"postgresql://{auth}@{host}"

# Initializing ORM completely separate from process.py
ORM(
    url=url,
    purge=True
)
