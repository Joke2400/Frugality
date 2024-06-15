"""Unit tests for the various parsing utilities (excluding store & product parsing)."""
import httpx
import json
from pytest import MonkeyPatch
from app.core import parse


def mock_json_load_raises_error() -> None:
    """Mock JSON load raises error."""
    raise json.JSONDecodeError(
        "Mock error", "", 0)


def test_prepare_response_dict_is_valid_json():
    """Unit test to test that valid json is returned properly."""
    response = httpx.Response(
        status_code=200,
        text='{"key": "value"}')
    result = parse.prepare_response_dict(response=response)
    assert result == {'key': 'value'}


def test_prepare_response_dict_is_invalid_json(monkeypatch: MonkeyPatch):
    """Unit test to test that invalid json returns as None"""
    monkeypatch.setattr(json, "load", mock_json_load_raises_error)
    response = httpx.Response(
        status_code=200,
        text="{'key': 'value'}")
    result = parse.prepare_response_dict(response=response)
    assert result is None
