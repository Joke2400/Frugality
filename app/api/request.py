"""HTTPX http functions."""
import json
from httpx import (
    AsyncClient,
    Response,
    Request,
    HTTPError,
    RequestError,
    ConnectError,
    ConnectTimeout
)
from app.core import config
from app.utils import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=0, fh=10)
DEBUG_FLAG = bool(config.parser["APP"]["debug"])


async def log_request(r: Request) -> None:
    """Log a HTTPX Request."""
    logger.debug(
        "[REQUEST] - Event hook: %s %s - Waiting for response.",
        r.method, r.url
    )


async def log_response(r: Response) -> None:
    """Log a HTTPX Response."""
    logger.debug(
        "[RESPONSE] - Event hook: %s %s - Status: %s",
        r.request.method, r.request.url, r.status_code
    )


async_client = AsyncClient(
    event_hooks={
        'response': [log_response],
        'request': [log_request]}
)


def handle_response(response: Response) -> bool:
    """Handle and log potential httpx response exceptions.

    Returns:
        Boolean indicates whether or not an exception occurred.
        True = No exception occurred
        False = Exception occurred
    """
    try:
        response.raise_for_status()

    except ConnectTimeout as err:
        logger.info(
            "Connection timed out: %s %s",
            err.request.method, err.request.url)

    except ConnectError as err:
        logger.info(
            "Could not establish connection to: %s %s",
            err.request.method, err.request.url)

    except (HTTPError, RequestError) as err:
        logger.exception(err)

    else:
        if DEBUG_FLAG:
            logger.debug("Received response: %s", json.dumps(
                json.loads(response.text), indent=4))
        return True
    return False


async def send_request(params: dict) -> Response | None:
    """Sends a request & raises the for status on the response.

    Returns an httpx.Response upon successful request.
    If an httpx exception occurred, returns None instead.
    """
    if DEBUG_FLAG:
        logger.debug("Sending request: %s", json.dumps(
            params, indent=4))
    response = await async_client.request(**params)
    if not handle_response(response):
        return None
    return response
