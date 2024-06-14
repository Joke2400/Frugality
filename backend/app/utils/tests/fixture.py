"""Contains ORM fixtures for testing."""
import pytest
from fastapi.testclient import TestClient
from app.core.process import Process
from app.core.orm import database
from app.utils.populate import populate_all


@pytest.fixture(scope="session")
def test_client():
    """Fixture that provides a FastAPI TestClient."""
    return TestClient(Process().app)


@pytest.fixture(scope="module")
def orm_populated_clean_slate():
    """Module-level fixture that ensures the database has consistent data."""
    database.ORM().purge_all()
    database.ORM().create_all()
    populate_all(database.ORM)


@pytest.fixture(scope="function")
def orm_create_and_purge():
    """Function-level fixture for managing ORM between tests.

    Creates tables, runs the function, then purges all tables."""
    database.ORM().create_all()
    yield
    database.ORM().purge_all()
