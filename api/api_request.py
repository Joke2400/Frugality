import json

from httpx import Client, AsyncClient
from httpx import HTTPError, RequestError, ConnectError, ConnectTimeout
from httpx import Response, Request

from utils import LoggerManager

query_logger = LoggerManager.get_logger(name="query", level=20)


def log_request(request: Request) -> None:
    """Log a request."""
    query_logger.debug(
        "Request event hook: %s %s - Waiting for response",
        request.method, request.url)


def log_response(response: Response) -> None:
    """Log a response."""
    request = response.request
    query_logger.debug(
        "Response event hook: %s %s - Status %s",
        request.method, request.url, response.status_code)


async def async_log_request(request: Request) -> None:
    """Log a request."""
    log_request(request)


async def async_log_response(response: Response) -> None:
    """Log a response."""
    log_response(response)


client = Client(
    event_hooks={'response': [log_response],
                 'request': [log_request]})

async_client = AsyncClient(
    event_hooks={'response': [async_log_response],
                 'request': [async_log_request]})


def post_request(url: str, params: dict,
                 do_logging: bool = False) -> Response | None:
    """Send a post request with JSON body to a given URL.

    Args:
        url and params are required as explicit parameters.
        params gets unpacked into the request as keyword arguments.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, returns None.
    """
    if do_logging:
        query_logger.debug("Parameters: %s", json.dumps(
            params, indent=4))
    response = client.post(
        url=url, **params)
    if not handle_response(response, do_logging):
        return None
    return response


async def async_post_request(url: str, params: dict,
                             do_logging: bool = False) -> Response | None:
    """Send a post request with JSON body to a given URL, async version.

    Args:
        url and params are required as explicit parameters.
        params gets unpacked into the request as keyword arguments.

    Returns:
        Response | None: Default returns a httpx.Response object.
        If an exception is raised, returns None.
    """
    if do_logging:
        query_logger.debug("Parameters: %s", json.dumps(
            params, indent=4))
    response = await async_client.post(
        url=url, **params)
    if not handle_response(response, do_logging):
        return None
    return response


def handle_response(response: Response, do_logging: bool = False
                    ) -> bool:
    """Handle and log potential httpx response exceptions.

    Returns:
        Boolean indicates whether or not an exception occurred.
        True = No exception occurred
        False = Exception occurred
    """
    try:
        response.raise_for_status()

    except ConnectTimeout as err:
        query_logger.info(
            "Connection timed out: %s %s",
            err.request.method, err.request.url)

    except ConnectError as err:
        query_logger.info(
            "Could not establish connection to: %s %s",
            err.request.method, err.request.url)

    except (HTTPError, RequestError) as err:
        query_logger.exception(err)

    else:
        if do_logging:
            query_logger.debug("Response: %s", json.dumps(
                json.loads(response.text), indent=4))
        return True
    return False
