import asyncio
import requests
import json

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm
from api import s_queries
from core import (
    ProductList,
)

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__)
query_logger = lgm.get_logger(name="query", level=20)


def send_post(query_string: str, params: dict) -> requests.Response:
    response = requests.post(url=api_url, json=params, timeout=1)
    logger.debug(
        f"Queried: '{query_string}', got response [{response.status_code}]")
    status = response.status_code
    response = json.loads(response.text)
    query_logger.debug(
        f"Queried: '{query_string}', got response" +
        f"[{status}]\nResponse text:" +
        json.dumps(response, indent=4))
    return response


async def async_send_post(query: str, variables: dict,
                          operation: str) -> requests.Response:
    params = {
        "query": query,
        "variables": variables,
        "operation_name": operation}
    query_string = variables["query"]
    response = await asyncio.to_thread(send_post, query_string, params)
    return response


async def parse_response(query: str, variables: dict,
                         operation: str) -> ProductList:
    response = await async_send_post(query, variables, operation)
    products = ProductList(
        response=response,
        query_string=variables["query"],
        category=variables["slugs"])
    logger.debug(
        f"Created ProductList from query string: '{variables['query']}'")
    return products


async def get_groceries(request, product_queries, limit=24):
    tasks = []
    operation = "GetProductByName"
    query = s_queries[operation]
    for c, p in enumerate(product_queries):
        variables = {
            "StoreID": request.json["store_id"],
            "limit": limit,
            "query": p.name,
            "slugs": p.category
        }
        logger.debug(
            f"Query @ index: {c} [Query: '{p.name}' " +
            f"Category: '{p.category}']")
        tasks.append(
            parse_response(
                query=query,
                variables=variables,
                operation=operation))
    logger.debug(
        f"Async tasks len(): {len(tasks)}\n")
    return await asyncio.gather(*tasks)