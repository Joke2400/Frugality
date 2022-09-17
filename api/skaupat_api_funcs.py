from core.app_dataclasses import ProductList
from data.urls import SKaupatURLs as s_urls
from api import queries
from utils import timer

import asyncio
from aiohttp import ClientSession

api_url = s_urls.api_url

async def send_post(session, query, operation_name, variables):
    response = await session.request(method="POST", url=api_url, json={
        "operationName": operation_name,
        "variables": variables,
        "query": query
    })
    response.raise_for_status()
    response = await response.text()
    return response

def send_get(operation_name, variables):
    pass
    #payload = {"operationName": operation_name, "variables": variables}
    #request = requests.get(url=api_url, params=payload)
    #return request

async def parse(session, query, operation_name, variables):
    result = await send_post(session, query, operation_name, variables)
    p = ProductList(result, variables["query"], variables["slugs"])
    print(p)

async def get_groceries(request, product_queries, limit=24):
    async with ClientSession() as session:
        tasks = []
        operation = "GetProductByName"
        query = queries[operation]
        for p in product_queries:
            variables = {
            "StoreID": request.json["store_id"],
            "limit": limit,
            "query": p.name,
            "slugs": p.category
            }
            tasks.append(
                parse(
                    session=session,
                    query=query,
                    operation_name=operation,
                    variables=variables))
        await asyncio.gather(*tasks)