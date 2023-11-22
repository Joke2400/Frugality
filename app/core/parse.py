import json
import httpx


def parse_store_response(response: httpx.Response | None):
    if response is not None:
        content = json.loads(response.text)