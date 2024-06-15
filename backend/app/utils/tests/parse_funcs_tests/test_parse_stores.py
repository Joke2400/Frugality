"""Contains unit tests for parsing stores from a httpx.Response."""
from typing import Any
from pytest import MonkeyPatch

from app.core import parse
from app.core.orm import schemas


def mock_response_dict_is_valid(*args: Any, **kwargs: Any) -> dict[Any, Any]:
    """Mock a valid API response dict."""
    return {
        "data": {
            "searchStores": {
                "stores": [
                    {
                        # More fields in real response
                        # This is what is currently used
                        "name": "Store Name 1",
                        "id": 123,
                        "slug": "store-name-1",
                        "brand": "Store Brand 1"
                    },
                    {
                        "name": "Store Name 2",
                        "id": 456,
                        "slug": "store-name-2",
                        "brand": "Store Brand 2"
                    }
                ]
            }
        }
    }


def mock_response_dict_has_invalid_item(
        *args: Any, **kwargs: Any) -> dict[Any, Any]:
    """Mock a valid API response dict."""
    return {
        "data": {
            "searchStores": {
                "stores": [
                    {
                        "name": "Store Name 1",
                        "id": 123,
                        "slug": "store-name-1",
                        "brand": "Store Brand 1"
                    },
                    {
                        "name": "Store Name 2",
                        "id": None,  # This data is of invalid type
                        "slug": "store-name-2",
                        "brand": "Store Brand 2"
                    }
                ]
            }
        }
    }


def mock_response_dict_has_missing_key(
        *args: Any, **kwargs: Any) -> dict[Any, Any]:
    """Mock a valid API response dict."""
    return {
        "data": {
            "searchStores": {}
        }
    }


def test_parse_store_response_default(monkeypatch: MonkeyPatch):
    """Test that the 'happy path' for parsing stores works as expected."""
    monkeypatch.setattr(
        parse, "prepare_response_dict", mock_response_dict_is_valid)
    # The response gets mocked & query is simply used for logging
    result = parse.parse_store_response(
        response=None, query="test")  # type: ignore
    assert result is not None
    assert isinstance(result[0], schemas.Store)
    assert len(result) == 2


def test_parse_store_response_could_not_parse_item(
        monkeypatch: MonkeyPatch):
    """Test that invalid items are dropped from returned list."""
    monkeypatch.setattr(
        parse, "prepare_response_dict", mock_response_dict_has_invalid_item)
    # The response gets mocked & query is simply used for logging
    result = parse.parse_store_response(
        response=None, query="test")  # type: ignore
    assert result is not None
    assert isinstance(result[0], schemas.Store)
    assert len(result) == 1


def test_parse_store_response_could_not_parse_dict(
        monkeypatch: MonkeyPatch):
    """Test that an unparseable response returns None."""
    monkeypatch.setattr(
        parse, "prepare_response_dict", lambda x: None)  # type: ignore
    # The response gets mocked & query is simply used for logging
    result = parse.parse_store_response(
        response=None, query="test")  # type: ignore
    assert result is None


def test_parse_store_response_missing_key(monkeypatch: MonkeyPatch):
    """Test that None is returned if the required key is not found."""
    monkeypatch.setattr(
        parse, "prepare_response_dict", mock_response_dict_has_missing_key)
    # The response gets mocked & query is simply used for logging
    result = parse.parse_store_response(
        response=None, query="test")  # type: ignore
    assert result is None
