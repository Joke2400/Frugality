"""Contains unit & integration tests for predefined crud operations."""
from typing import Any
from datetime import datetime
from pytest import MonkeyPatch
from pydantic import ValidationError
from app.core.orm import crud, models, schemas, operations, database
from app.utils.populate import populate_all

from .fixture import setup_and_teardown


def return_single_store_record(*args: Any, **kwargs: Any):
    """Mock for when crud returns a single store model."""
    return models.Store(
        id=1,
        store_id=123,
        store_name="Test Store",
        slug="test-store",
        brand="Test",
        timestamp=datetime.now()
    )


def return_multiple_store_records(*args: Any, **kwargs: Any):
    """Mock for when crud returns multiple store models."""
    return [
        models.Store(
            id=1,
            store_id=123,
            store_name="Test Store 1",
            slug="test-store-1",
            brand="Test",
            timestamp=datetime.now()
        ),
        models.Store(
            id=2,
            store_id=456,
            store_name="Test Store 2",
            slug="test-store-2",
            brand="Test",
            timestamp=datetime.now()
        ),
        models.Store(
            id=3,
            store_id=789,
            store_name="Test Store 3",
            slug="test-store-3",
            brand="Test",
            timestamp=datetime.now()
        )
    ]


def return_single_product_record(*args: Any, **kwargs: Any):
    """Mock for when crud returns a single product model."""
    return models.Product(
        id=1,
        ean="1234567890",
        name="Test Product",
        slug="test-product",
        category="Test Products",
        brand='Test',
        timestamp=datetime.now()
    )


def return_multiple_product_records(*args: Any, **kwargs: Any):
    """Mock for when crud returns multiple product models."""
    return [
        models.Product(
            id=1,
            ean="123",
            name="Test Product 1",
            slug="test-product-1",
            category="Test Products",
            brand='Test',
            timestamp=datetime.now()
        ),
        models.Product(
            id=2,
            ean="456",
            name="Test Product 2",
            slug="test-product-2",
            category="Test Products",
            brand='Test',
            timestamp=datetime.now()
        ),
        models.Product(
            id=3,
            ean="789",
            name="Test Product 3",
            slug="test-product-3",
            category="Test Products",
            brand='Test',
            timestamp=datetime.now()
        )
    ]


def throw_pydantic_validation_error(*args: Any, **kwargs: Any):
    """Mock that simply throws a ValidationError."""
    raise ValidationError.from_exception_data(
        'Test Error', [], hide_input=True)


def test_get_store_by_id_default(monkeypatch: MonkeyPatch):
    """Test get_store_by_id default behaviour."""
    monkeypatch.setattr(crud, "read_one", return_single_store_record)
    # The input param does not matter here
    result = operations.get_store_by_id(store_id=123)
    assert isinstance(result, schemas.StoreDB)


def test_get_store_by_id_no_result(monkeypatch: MonkeyPatch):
    """Test get_store_by_id returns no result."""
    monkeypatch.setattr(crud, "read_one", lambda stmt, session_ctx: None)
    # The input param does not matter here
    result = operations.get_store_by_id(store_id=123)
    assert result is None


def test_get_store_by_id_validation_fail(monkeypatch: MonkeyPatch):
    """Test get_store_by_id pydantic validation error occurs."""
    monkeypatch.setattr(crud, "read_one", return_single_store_record)
    monkeypatch.setattr(schemas.StoreDB, "model_validate",
                        throw_pydantic_validation_error)
    # The input param does not matter here
    result = operations.get_store_by_id(store_id=123)
    assert result is None


def test_get_store_by_id_integration(setup_and_teardown):
    """Integration test for get_store_by_id."""
    populate_all(database.ORM)
    result = operations.get_store_by_id(store_id=542862479)
    assert isinstance(result, schemas.StoreDB)
    assert result.store_id == 542862479


def test_get_stores_by_name_default(monkeypatch: MonkeyPatch):
    """Test get_stores_by_name default behaviour."""
    monkeypatch.setattr(crud, "read_all", return_multiple_store_records)
    # The input param does not matter here
    result = operations.get_stores_by_name(name="", brand='')
    for i in result:
        assert isinstance(i, schemas.StoreDB)


def test_get_stores_by_name_no_result(monkeypatch: MonkeyPatch):
    """Test get_stores_by_name returns no result."""
    monkeypatch.setattr(crud, "read_all", lambda stmt, session_ctx: [])
    # The input param does not matter here
    result = operations.get_stores_by_name(name="", brand='')
    assert result == []


def test_get_stores_by_name_validation_fail(monkeypatch: MonkeyPatch):
    """Test get_stores_by_name pydantic validation error occurs."""
    monkeypatch.setattr(crud, "read_all", return_multiple_store_records)
    monkeypatch.setattr(schemas.StoreDB, "model_validate",
                        throw_pydantic_validation_error)
    # The input param does not matter here
    result = operations.get_stores_by_name(name="", brand='')
    assert result == []


def test_get_stores_by_name_integration(setup_and_teardown):
    """Integration test for get_stores_by_name."""
    populate_all(database.ORM)
    result = operations.get_stores_by_name(name="Prisma")
    assert len(result) == 2
    for i in result:
        assert isinstance(i, schemas.StoreDB)
        assert "Prisma" in i.store_name


def test_get_product_by_ean_default(monkeypatch: MonkeyPatch):
    """Test get_product_by_ean default behaviour."""
    monkeypatch.setattr(crud, "read_one", return_single_product_record)
    # The input param does not matter here
    result = operations.get_product_by_ean(ean="123")
    assert isinstance(result, schemas.ProductDB)


def test_get_product_by_ean_no_result(monkeypatch: MonkeyPatch):
    """Test get_product_by_ean returns no result."""
    monkeypatch.setattr(crud, "read_one", lambda stmt, session_ctx: None)
    # The input param does not matter here
    result = operations.get_product_by_ean(ean="123")
    assert result is None


def test_get_product_by_ean_validation_fail(monkeypatch: MonkeyPatch):
    """Test get_product_by_ean pydantic validation error occurs."""
    monkeypatch.setattr(crud, "read_one", return_single_product_record)
    monkeypatch.setattr(schemas.ProductDB, "model_validate",
                        throw_pydantic_validation_error)
    # The input param does not matter here
    result = operations.get_product_by_ean(ean="123")
    assert result is None


def test_get_product_by_ean_integration(setup_and_teardown):
    """Integration test for get_product_by_ean."""
    populate_all(database.ORM)
    result = operations.get_product_by_ean(ean="6414893500167")
    assert isinstance(result, schemas.ProductDB)
    assert result.ean == "6414893500167"


def test_get_products_by_name_default(monkeypatch: MonkeyPatch):
    """Test get_products_by_name default behaviour."""
    monkeypatch.setattr(crud, "read_all", return_multiple_product_records)
    # The input param does not matter here
    result = operations.get_products_by_name(name="", category='')
    for i in result:
        assert isinstance(i, schemas.ProductDB)


def test_get_products_by_name_no_result(monkeypatch: MonkeyPatch):
    """Test get_products_by_name returns no result."""
    monkeypatch.setattr(crud, "read_all", lambda stmt, session_ctx: [])
    # The input param does not matter here
    result = operations.get_products_by_name(name="", category='')
    assert result == []


def test_get_products_by_name_validation_fail(monkeypatch: MonkeyPatch):
    """Test get_product_by_name pydantic validation error occurs."""
    monkeypatch.setattr(crud, "read_all", return_multiple_product_records)
    monkeypatch.setattr(schemas.ProductDB, "model_validate",
                        throw_pydantic_validation_error)
    # The input param does not matter here
    result = operations.get_products_by_name(name="", category='')
    assert result == []


def test_get_products_by_name_integration(setup_and_teardown):
    """Integration test for get_products_by_name."""
    populate_all(database.ORM)
    result = operations.get_products_by_name(name="Kotimaista")
    assert len(result) == 2
    for i in result:
        assert isinstance(i, schemas.ProductDB)
        assert "Kotimaista" in i.name
