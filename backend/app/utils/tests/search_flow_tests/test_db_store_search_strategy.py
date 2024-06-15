"""Contains unit tests for DBStoreSearchStrategy."""
from typing import Any, TypeAlias
from datetime import datetime
from pytest import MonkeyPatch

from app.core.search.store_flow import DBStoreSearchStrategy
from app.core.search.state import SearchState
from app.core.orm import schemas
from app.utils.util_funcs import assert_never
from app.core.orm import operations

StoreDB: TypeAlias = schemas.StoreDB[schemas.ProductDataDB]


def returns_single_store(
        *args: Any, **kwargs: Any) -> StoreDB:
    """Mock for when the DB returns a result."""
    return schemas.StoreDB[schemas.ProductDataDB](
        store_name="Store Name",
        store_id=123,
        slug="store-name",
        brand="Store",
        id=1,
        timestamp=datetime.now(),
    )


def returns_list_of_stores(*args: Any, **kwargs: Any) -> list[StoreDB]:
    """Mock for when the DB returns multiple results."""
    return [
        schemas.StoreDB[schemas.ProductDataDB](
            id=1,
            store_name="Store Name 1",
            store_id=123,
            slug="store-name-1",
            brand="Store",
            timestamp=datetime.now()
        ),
        schemas.StoreDB[schemas.ProductDataDB](
            id=2,
            store_name="Store Name 2",
            store_id=456,
            slug="store-name-2",
            brand="Store",
            timestamp=datetime.now()
        ),
        schemas.StoreDB[schemas.ProductDataDB](
            id=3,
            store_name="Store Name 3",
            store_id=789,
            slug="store-name-3",
            brand="Store",
            timestamp=datetime.now()
        )
    ]


async def test_search_by_name_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store name is passed in."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(operations, "get_stores_by_name",
                        returns_list_of_stores)
    monkeypatch.setattr(operations, "get_store_by_id", assert_never)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], schemas.StoreDB)
    assert len(result[1]) == 3


async def test_search_by_id_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store id is passed in."""
    query = schemas.StoreQuery(store_name=None, store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", returns_single_store)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], schemas.StoreDB)
    assert len(result[1]) == 1


async def test_search_by_both_default(monkeypatch: MonkeyPatch):
    """Testcase for when both name and id are passed in."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", returns_single_store)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], schemas.StoreDB)
    assert len(result[1]) == 1


async def test_name_search_no_result(monkeypatch: MonkeyPatch):
    """Testcase for when name search yields no results."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(operations, "get_stores_by_name", lambda x: [])
    monkeypatch.setattr(operations, "get_store_by_id", assert_never)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.FAIL
    assert len(result[1]) == 0


async def test_id_search_no_result(monkeypatch: MonkeyPatch):
    """Testcase for when id search yields no results."""
    query = schemas.StoreQuery(store_name=None, store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", lambda x: None)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.FAIL
    assert len(result[1]) == 0
