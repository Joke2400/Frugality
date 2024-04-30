"""Contains ORM fixtures for testing."""
import pytest
from app.core.orm import database
from app.utils import config, util_funcs

# Initializing ORM completely separate from process.py
database.ORM(
    url=util_funcs.build_db_url(
        usr=config.ENV().postgres_user,
        passwd=config.ENV().postgres_password,
        db=config.ENV().postgres_db,
        testing=True),
    _purge=True
)


@pytest.fixture(scope="function")
def setup_and_teardown():
    """Create tables on setup & purge tables on teardown."""
    database.ORM().create_all()
    yield
    database.ORM().purge_all()
