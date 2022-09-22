import asyncio
import requests

from data.urls import SKaupatURLs as s_urls
from utils import LoggerManager as lgm
from api import s_queries
from core import (
    ProductList,
    AmountTuple,
    get_quantity,
    get_specifiers,
    QueryItem
)

api_url = s_urls.api_url
logger = lgm.get_logger(name=__name__, level=20, stream=True)


def send_post(query_string: str, params: dict) -> requests.Response:
    response = requests.post(url=api_url, json=params, timeout=1)
    logger.debug(f"Query: {query_string} Response: {response}")
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
            f"List index: {c} [Query: '{p.name}' " +
            "Category: '{p.category}']")
        tasks.append(
            parse_response(
                query=query,
                variables=variables,
                operation=operation))
    logger.debug(
        f"Tasks len(): {len(tasks)}")
    return await asyncio.gather(*tasks)


def parse_input(request):
    product_queries = []
    logger.debug("Parsing user input...")
    for query, amt, cat in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
        if query == "" or query is None:
            logger.debug(
                "Received an empty query, skipping...")
            continue

        try:
            if amt != "" and amt is not None:
                amt = int(amt)
        except ValueError:
            logger.exception(
                "Amt could not be converted to 'int'")
            amt = 1
        tup = AmountTuple(amount=amt, **get_quantity(query))
        contain = get_specifiers(query)

        product_queries.append(
            QueryItem(
                name=query,
                amt=tup,
                category=cat,
                must_contain=contain))

    logger.debug(
        f"product_queries len(): {len(product_queries)}")
    return product_queries
