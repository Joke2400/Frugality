"""Main file for Flask app, contains all the app routes."""

import json
import asyncio
from flask import url_for, render_template
from flask import request, session, Blueprint

from utils import LoggerManager
from utils import Success, Fail, ParseFailed, NoResponse

from .store_flow import execute_store_search
from .store_flow import add_store_query
from .store_flow import remove_store_query

from .product_flow import execute_product_search
from .product_flow import add_product_query
from .product_flow import remove_product_query
from .search import Search
from .store import Store


logger = LoggerManager.get_logger(name=__name__)
app = Blueprint(name="Frugality", import_name=__name__)
loop = asyncio.get_event_loop()


@app.route("/", methods=["GET"])
def index_page():
    """Return a template for the main page."""
    products = session.get("products", default=[])
    stores = session.get("stores", default=[])
    return render_template(
        "index.html",
        products=products,
        stores=stores), 200


@app.route("/results/", methods=["GET"])
def results_page():
    """Return a template for the results page."""
    return render_template(
        "results.html"), 200


@app.route("/stores/", methods=["GET"])
def fetch_stores():
    """Return session stores."""
    stores = session.get("stores", default=[])
    return {"stores": stores}, 200


@app.route("/products/", methods=["GET"])
def fetch_products():
    """Return session products."""
    products = session.get("products", default=[])
    return {"products": products}, 200


@app.route("/store/query/", methods=["POST"])
def store_query():
    """Execute a search for a store."""
    search: Search = execute_store_search(
        value=request.json.get("value", None))
    match search.state:

        case Success():
            return {
                "message": f"Success! Found: {len(search.result)} stores.",
                "stores": search.result
            }, 200

        case Fail():
            return {
                "message":
                    f"No results received: {search.query}."
            }, 404

        case ParseFailed():
            return {
                "message": search.feedback
            }, 400

        case NoResponse():
            return {
                "message":
                    "Response from API call was empty or invalid."
            }, 500
        case _:
            return {
                "message": "Unknown server error."}, 500


@app.route("/store/query/select/", methods=["DELETE", "POST"])
def modify_store_queries():
    """Add or remove a store query from user session.

    Which action to take is determined by the method
    used in the request (POST = ADD).

    Adding requires a tuple in the form: (name, id, slug),
    to be present in the "store" key.

    Removing requires a store id string to be present in
    the "id" key.
    """
    stores = session.get("stores", default=[])
    if request.method == "DELETE":
        stores, status = remove_store_query(request.json, stores)
    else:
        stores, status = add_store_query(request.json, stores)
    if status in (200, 201):
        session["stores"] = stores
    return {"result": stores}, status


@app.route("/product/query/", methods=["GET"])
def product_query():
    """Execute a product search with session stores/products."""
    if len(stores := session.get("stores", default=[])) == 0:
        return url_for(".main_page")
    if len(queries := session.get("products", default=[])) == 0:
        return url_for(".main_page")

    # Expensive operation, Store class will be reworked later
    stores: list[Store] = [Store(x, y, z) for x, y, z in stores]

    results = loop.run_until_complete(
        execute_product_search(queries=queries, stores=stores))
    return {
        "url": url_for(".results_page"),
        "results": results}, 200


@app.route("/product/query/select/", methods=["DELETE", "POST"])
def modify_product_queries():
    """Add or remove a product query from user session.

    Which action to take is determined by the method
    used in the request (POST = ADD).

    Adding requires a string to be present in the "product" key.

    Removing requires a string to be present in the "slug" key.
    """
    products = session.get("products", default=[])

    if request.method == "DELETE":
        products, status = remove_product_query(request.json, products)
    else:
        products, status = add_product_query(request.json, products)
    if status in (200, 201):
        session["products"] = products
    return {"result": products}, status
