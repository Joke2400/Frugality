"""Contains tests for testing the DB store search strategy."""
from typing import Any
from datetime import datetime
from pytest import MonkeyPatch

from app.core.search.store_flow import DBStoreSearchStrategy
from app.core.search.state import SearchState
from app.core.orm.schemas import (
    StoreQuery,
    StoreDB,
    Store,
    ProductDataDB
)
from app.utils.util_funcs import assert_never
from app.core.orm import operations


def returns_single_store(*args: Any, **kwargs: Any) -> StoreDB[ProductDataDB]:
    """Mock for when the DB returns a result."""
    return StoreDB[ProductDataDB](
        store_name="Store Name",
        store_id=123,
        slug="store-name",
        brand="Store",
        id=1,
        timestamp=datetime.now(),
    )


def returns_list_of_stores(*args: Any, **kwargs: Any) -> list[Store]:
    """Mock for when the DB returns multiple results."""
    return [
        Store(
            store_name="Store Name 1",
            store_id=123,
            slug="store-name-1",
            brand="Store",
        ),
        Store(
            store_name="Store Name 2",
            store_id=456,
            slug="store-name-2",
            brand="Store",
        ),
        Store(
            store_name="Store Name 3",
            store_id=789,
            slug="store-name-3",
            brand="Store",
        )
    ]


async def test_search_by_name_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store name is passed in."""
    query = StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(operations, "get_stores_by_name",
                        returns_list_of_stores)
    monkeypatch.setattr(operations, "get_store_by_id", assert_never)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], Store)
    assert len(result[1]) == 3


async def test_search_by_id_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store id is passed in."""
    query = StoreQuery(store_name=None, store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", returns_single_store)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], StoreDB)
    assert len(result[1]) == 1


async def test_search_by_both_default(monkeypatch: MonkeyPatch):
    """Testcase for when both name and id are passed in."""
    query = StoreQuery(store_name="Store Name", store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", returns_single_store)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], StoreDB)
    assert len(result[1]) == 1


async def test_name_search_no_result(monkeypatch: MonkeyPatch):
    """Testcase for when name search yields no results."""
    query = StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(operations, "get_stores_by_name", lambda x: [])
    monkeypatch.setattr(operations, "get_store_by_id", assert_never)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.FAIL
    assert len(result[1]) == 0


async def test_id_search_no_result(monkeypatch: MonkeyPatch):
    """Testcase for when id search yields no results."""
    query = StoreQuery(store_name=None, store_id=123)
    monkeypatch.setattr(operations, "get_stores_by_name", assert_never)
    monkeypatch.setattr(operations, "get_store_by_id", lambda x: None)
    result = await DBStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.FAIL
    assert len(result[1]) == 0
