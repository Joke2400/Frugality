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
from app.utils import LoggerManager

logger = LoggerManager().get_logger(path=__name__, sh=20, fh=10)


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


async def send_request(method: str, url: str3):
    request = async_client.request(
        method=method,
        url=url,
        
    )