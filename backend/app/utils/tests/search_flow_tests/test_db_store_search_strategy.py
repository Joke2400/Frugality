"""Contains tests for testing the DB store search strategy."""
from datetime import datetime
from pytest import MonkeyPatch

from backend.app.core.store_search import DBStoreSearchStrategy
from backend.app.core.search_context import (
    SearchContext,
    DBSearchState,
)
from backend.app.core.orm.schemas import (
    StoreQuery,
    StoreDB,
    Store
)
from backend.app.utils.util_funcs import assert_never

import backend.app.core.orm.crud as crud


def crud_returns_single_store(*args, **kwargs):
    """Mock for when the DB returns a result."""
    return StoreDB(
        store_name="Store Name",
        store_id=123,
        slug="store-name",
        brand="Store",
        id=1,
        timestamp=datetime.now(),
    )


def crud_returns_list_of_stores(*args, **kwargs):
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


async def test_db_search_by_name_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store name is passed in."""
    query = StoreQuery(store_name="Store Name", store_id=None)
    # DB search should not interact with fields other than query
    context = SearchContext(
        query=query, strategy=None, task=None)  # type: ignore
    monkeypatch.setattr(crud, "get_stores_by_name",
                        crud_returns_list_of_stores)
    monkeypatch.setattr(crud, "get_store_by_id", assert_never)
    result = await DBStoreSearchStrategy.execute(context=context)
    assert result[0] is DBSearchState.SUCCESS
    assert isinstance(result[1], list)
    assert isinstance(result[1][0], Store)


async def test_db_search_by_id_default(monkeypatch: MonkeyPatch):
    """Testcase for when only a store id is passed in."""
    query = StoreQuery(store_name=None, store_id=123)
    # DB search should not interact with fields other than query
    context = SearchContext(
        query=query, strategy=None, task=None)  # type: ignore
    monkeypatch.setattr(crud, "get_stores_by_name", assert_never)
    monkeypatch.setattr(crud, "get_store_by_id", crud_returns_single_store)
    result = await DBStoreSearchStrategy.execute(context=context)
    assert result[0] is DBSearchState.SUCCESS
    print(result[1])
    assert isinstance(result[1][0], StoreDB)


async def test_db_search_by_both_default(monkeypatch: MonkeyPatch):
    """Testcase for when both name and id are passed in."""
    query = StoreQuery(store_name="Store Name", store_id=123)
    # DB search should not interact with fields other than query
    context = SearchContext(
        query=query, strategy=None, task=None)  # type: ignore
    monkeypatch.setattr(crud, "get_stores_by_name", assert_never)
    monkeypatch.setattr(crud, "get_store_by_id", crud_returns_single_store)
    result = await DBStoreSearchStrategy.execute(context=context)
    assert result[0] is DBSearchState.SUCCESS
    assert isinstance(result[1][0], StoreDB)


