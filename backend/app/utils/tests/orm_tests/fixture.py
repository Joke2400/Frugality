"""Contains ORM fixtures for testing."""
import pytest
from backend.app.core.orm import database

# Initializing ORM completely separate from process.py
# module __init__ fetches envvars & creates url to 'test_database'
# TODO: Re-evaluate if this is a smart thing to do in terms of security.
# (not that envvars should be used anyway; Is a problem for the future me.)
from . import _url
database.ORM(
    url=_url,
    _purge=True
)


@pytest.fixture(scope="function")
def setup_and_teardown():
    """Create tables on setup & purge tables on teardown."""
    database.ORM().create_all()
    yield
    database.ORM().purge_all()
