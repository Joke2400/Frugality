import asyncio
import requests

from data.urls import SKaupatURLs as s_urls
from api import s_queries
from core import (
    ProductList,
    AmountTuple,
    get_quantity,
    get_specifiers,
    QueryItem
)

api_url = s_urls.api_url


def send_post(**kwargs) -> requests.Response:
    response = requests.post(url=api_url, json=kwargs, timeout=1)
    return response


def send_get(**kwargs) -> requests.Response:
    response = requests.get(url=api_url, params=kwargs, timeout=1)
    return response


async def async_send_post(**kwargs) -> requests.Response:
    response = await asyncio.to_thread(send_post, **kwargs)
    return response


async def async_send_get(**kwargs) -> requests.Response:
    response = await asyncio.to_thread(send_get, **kwargs)
    return response


async def parse_response(**kwargs):
    response = await async_send_post(**kwargs)
    products = ProductList(
        response=response,
        query_string=kwargs.get("variables")["query"],
        category=kwargs.get("variables")["slugs"])
    return products


async def get_groceries(request, product_queries, limit=24):
    tasks = []
    operation = "GetProductByName"
    query = s_queries[operation]
    for p in product_queries:
        variables = {
            "StoreID": request.json["store_id"],
            "limit": limit,
            "query": p.name,
            "slugs": p.category
        }
        tasks.append(
            parse_response(
                query=query,
                operation_name=operation,
                variables=variables))
    return await asyncio.gather(*tasks)


def parse_input(request):
    product_queries = []
    for query, amt, cat in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
        if query == "":
            continue
        amt = int(amt) if amt != "" else 1
        tup = AmountTuple(amount=amt, **get_quantity(query))
        contain = get_specifiers(query)
        product_queries.append(
            QueryItem(
                name=query,
                amt=tup,
                category=cat,
                must_contain=contain))
    return product_queries
