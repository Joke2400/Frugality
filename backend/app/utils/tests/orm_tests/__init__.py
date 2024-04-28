from app.utils.util_funcs import get_envvar

_postgres_user = get_envvar("POSTGRES_USER")
_postgres_password = get_envvar("POSTGRES_PASSWORD")
_postgres_port = get_envvar("POSTGRES_PORT")

_auth = f"{_postgres_user}:{_postgres_password}"
_host = f"localhost:{_postgres_port}/test_database"
_url = f"postgresql://{_auth}@{_host}"
