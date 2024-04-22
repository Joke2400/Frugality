"""Contains tests for crud operations"""
from sqlalchemy.exc import DataError, IntegrityError
from backend.app.utils.util_funcs import cleanup, log_test_name
from backend.app.core.orm import crud, models, database


@cleanup
@log_test_name
def test_create_default():
    """Test the successful creation of a record."""
    store = models.Store(
        store_name="Test Store 1",
        store_id=123,
        slug="test-store-1",
        brand="test"
    )
    ctx = database.ORM().get_session_context(read_only=False)
    result = crud.create(record=store, session_ctx=ctx)
    assert result is store


@cleanup
@log_test_name
def test_create_invalid_data():
    """Test create when an error is raised."""
    store_1 = models.Store(
        store_name="Test Store 1",
        store_id="INVALID DATA",  # Note the incorrect value
        slug="test-store-1",
        brand="test"
    )
    ctx = database.ORM().get_session_context(read_only=False)
    result = crud.create(record=store_1, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is DataError


@cleanup
@log_test_name
def test_create_duplicate_data():
    """Test for failure on IntegrityError"""
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
    ctx = database.ORM().get_session_context(
        read_only=False, close_on_exit=False)
    result = crud.create(record=store_1, session_ctx=ctx)
    assert result is store_1
    result = crud.create(record=store_2, session_ctx=ctx)
    assert result is None
    assert ctx.prev_exc is IntegrityError
