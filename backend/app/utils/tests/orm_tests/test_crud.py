"""Contains tests for crud operations"""
import pytest
from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError, MultipleResultsFound
from backend.app.core.orm import crud, models, database
from backend.app.utils.populate import populate_stores


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


def test_create_default(setup_and_teardown):
    """Test crud create default behaviour."""
    store = models.Store(
        store_name="Test Store 1",
        store_id=123,
        slug="test-store-1",
        brand="test"
    )
    ctx = database.ORM().get_session_context()
    result = crud.create(record=store, session_ctx=ctx)
    assert result is store


def test_create_invalid_data(setup_and_teardown):
    """Test crud create fails with invalid data."""
    store_1 = models.Store(
        store_name="Test Store 1",
        store_id="INVALID DATA",  # Note the incorrect value
        slug="test-store-1",
        brand="test"
    )
    ctx = database.ORM().get_session_context()
    result = crud.create(record=store_1, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is DataError


def test_create_duplicate_data(setup_and_teardown):
    """Test crud create fails with duplicate data."""
    store_1 = models.Store(
        store_name="Test Store 1",
        store_id=123,
        slug="test-store-1",
        brand="test"
    )
    store_2 = models.Store(
        store_name="Test Store 1",
        store_id=123,
        slug="test-store-1",
        brand="test"
    )
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.create(record=store_1, session_ctx=ctx)
    assert result is store_1
    result = crud.create(record=store_2, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is IntegrityError


def test_insert_default(setup_and_teardown):
    """Test crud insert default behaviour."""
    store_1_dict = {
        "store_name": "Test Store 1",
        "store_id": 123,
        "slug": "test-store-1",
        "brand": "test"
    }

    store_2_dict = {
        "store_name": "Test Store 2",
        "store_id": 456,
        "slug": "test-store-2",
        "brand": "test"
    }

    store_3_dict = {
        "store_name": "Test Store 3",
        "store_id": 789,
        "slug": "test-store-3",
        "brand": "test"
    }
    stores = [store_1_dict, store_2_dict, store_3_dict]
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.insert(table=models.Store, records=stores, session_ctx=ctx)
    assert result is True
    with ctx:
        stmt = select(models.Store)
        all_stores = ctx.session.scalars(stmt).all()
        assert len(all_stores) == 3
    ctx.session.close()


def test_insert_invalid_data(setup_and_teardown):
    """Test crud insert fails with invalid data."""
    store_1_dict = {
        "store_name": "Test Store 1",
        "store_id": "INVALID DATA",
        "slug": "test-store-1",
        "brand": "test"
    }

    store_2_dict = {
        "store_name": "Test Store 2",
        "store_id": 456,
        "slug": "test-store-2",
        "brand": "test"
    }

    store_3_dict = {
        "store_name": "Test Store 3",
        "store_id": 789,
        "slug": "test-store-3",
        "brand": "test"
    }
    stores = [store_1_dict, store_2_dict, store_3_dict]
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.insert(table=models.Store, records=stores, session_ctx=ctx)
    assert result is False
    assert ctx.prev_exc is DataError
    with ctx:
        stmt = select(models.Store)
        all_stores = ctx.session.scalars(stmt).all()
        assert len(all_stores) == 0
    ctx.session.close()


def test_insert_duplicate_data(setup_and_teardown):
    """Test crud insert fails with duplicate value."""
    store_1_dict = {
        "store_name": "Test Store 1",
        "store_id": 123,
        "slug": "test-store-1",
        "brand": "test"
    }

    store_2_dict = {
        "store_name": "Test Store 2",
        "store_id": 456,
        "slug": "test-store-2",
        "brand": "test"
    }

    store_3_dict = {
        "store_name": "Test Store 2",
        "store_id": 456,
        "slug": "test-store-2",
        "brand": "test"
    }
    stores = [store_1_dict, store_2_dict, store_3_dict]
    ctx = database.ORM().get_session_context(close_on_exit=False)
    result = crud.insert(table=models.Store, records=stores, session_ctx=ctx)
    assert result is False
    assert ctx.prev_exc is IntegrityError
    with ctx:
        stmt = select(models.Store)
        all_stores = ctx.session.scalars(stmt).all()
        assert len(all_stores) == 0
    ctx.session.close()


def test_read_one_default(setup_and_teardown):
    """Test crud read_one default behaviour."""
    # Populate database with a consistent set of data
    populate_stores(orm=database.ORM)
    stmt = select(models.Store).where(models.Store.store_id == 542862479)
    ctx = database.ORM().get_session_context()
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    assert isinstance(result, models.Store)
    assert result.store_id == 542862479


def test_read_one_multiple_results(setup_and_teardown):
    """Test crud read_one fails when multiple results found."""
    # Populate database with a consistent set of data
    populate_stores(orm=database.ORM)
    # The query selects all stores while read_one calls one_or_none()
    stmt = select(models.Store)
    ctx = database.ORM().get_session_context()
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is MultipleResultsFound


def test_read_one_no_result(setup_and_teardown):
    """Test crud read_one returns no result (and no error)."""
    # Populate database with a consistent set of data
    populate_stores(orm=database.ORM)
    stmt = select(models.Store).where(models.Store.store_id == 123)
    ctx = database.ORM().get_session_context()
    result = crud.read_one(stmt=stmt, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is None


def test_read_all_default(setup_and_teardown):
    """Test crud read_all default behaviour."""
    # Populate database with a consistent set of data
    populate_stores(orm=database.ORM)
    stmt = select(models.Store)
    ctx = database.ORM().get_session_context()
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    assert len(result) == 4


def test_read_all_no_result(setup_and_teardown):
    """"Test crud read_all returns no results (and no error)."""
    # Populate database with a consistent set of data
    populate_stores(orm=database.ORM)
    stmt = select(models.Store).where(models.Store.store_id == 123)
    ctx = database.ORM().get_session_context()
    result = crud.read_all(stmt=stmt, session_ctx=ctx)
    assert len(result) == 0
    assert ctx.prev_exc is None
