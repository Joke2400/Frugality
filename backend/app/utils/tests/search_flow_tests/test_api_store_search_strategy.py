"""Contains unit tests for APIStoreSearchStrategy."""
from typing import Any
import httpx
from pytest import MonkeyPatch
from app.core import parse
from app.core.orm import schemas
from app.core.search.store_flow import APIStoreSearchStrategy
from app.core.search.state import SearchState
from app.utils.util_funcs import assert_never


async def mock_got_response(*args: Any, **kwargs: Any) -> httpx.Response:
    """Mock for when _send_store_query() returns a httpx.Response."""
    return httpx.Response(status_code=200)


async def mock_no_response(*args: Any, **kwargs: Any) -> None:
    """Mock for when _send_store_query() returns None."""
    return None


def mock_parsing_is_successful(
        *args: Any, **kwargs: Any) -> list[schemas.Store]:
    """Mock for when parse_store_response() is successful."""
    return [
        schemas.Store(
            store_name="Store Name 1",
            store_id=123,
            slug="store-name-1",
            brand="Store",
        ),
        schemas.Store(
            store_name="Store Name 2",
            store_id=456,
            slug="store-name-2",
            brand="Store",
        ),
        schemas.Store(
            store_name="Store Name 3",
            store_id=789,
            slug="store-name-3",
            brand="Store",
        )
    ]


async def test_search_default(monkeypatch: MonkeyPatch):
    """Unit test for 'happy path' of strategy."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(
        APIStoreSearchStrategy, "_send_store_query", mock_got_response)
    monkeypatch.setattr(
        parse, "parse_store_response", mock_parsing_is_successful)
    result = await APIStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.SUCCESS
    assert isinstance(result[1][0], schemas.Store)
    assert len(result[1]) == 3


async def test_search_no_results(monkeypatch: MonkeyPatch):
    """Unit test for when search returns empty list."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(
        APIStoreSearchStrategy, "_send_store_query", mock_got_response)
    monkeypatch.setattr(
        parse, "parse_store_response", lambda x, y: [])  # type: ignore
    result = await APIStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.FAIL
    assert len(result[1]) == 0


async def test_search_parse_error(monkeypatch: MonkeyPatch):
    """Unit test for when response cannot be parsed."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(
        APIStoreSearchStrategy, "_send_store_query", mock_got_response)
    monkeypatch.setattr(
        parse, "parse_store_response", lambda x, y: None)  # type: ignore
    result = await APIStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.PARSE_ERROR
    assert len(result[1]) == 0


async def test_search_no_response(monkeypatch: MonkeyPatch):
    """Unit test for when API returned no response."""
    query = schemas.StoreQuery(store_name="Store Name", store_id=None)
    monkeypatch.setattr(
        APIStoreSearchStrategy, "_send_store_query", mock_no_response)
    monkeypatch.setattr(
        parse, "parse_store_response", assert_never)  # raises assertion error
    result = await APIStoreSearchStrategy.execute(query=query)
    assert result[0] is SearchState.NO_RESPONSE
    assert len(result[1]) == 0
