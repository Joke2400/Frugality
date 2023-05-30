"""Main file for Flask app, contains all the app routes."""

import asyncio
from flask import redirect, url_for, render_template
from flask import request, session, Blueprint

from utils import LoggerManager
from utils import Success, NoResults, ParseFailed, NoResponse

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
def main_page():
    """Return a template for the main page."""
    products = session.get("products", default=[])
    stores = session.get("stores", default=[])
    return render_template(
        "index.html",
        products=products,
        stores=stores)


@app.route("/store/", methods=["GET"])
def store_page():
    """Return a template for the store page."""
    return "PAGE NOT IMPLEMENTED"


@app.route("/product/", methods=["GET"])
def product_page():
    """Return a template for the product page."""
    return "PAGE NOT IMPLEMENTED"


@app.route("/results/", methods=["GET"])
def results_page():
    """Return a template for the results page."""
    results = session.get("results", default=[])
    return render_template(
        "results.html",
        results=results)


@app.route("/stores/", methods=["GET"])
def get_stores():
    """Return session stores."""
    stores = session.get("stores", default=[])
    return {"stores": stores}


@app.route("/products/", methods=["GET"])
def get_products():
    """Return session products."""
    products = session.get("products", default=[])
    return {"products": products}


@app.route("/store/query/", methods=["GET"])
def store_query():
    search: Search = execute_store_search(
        value=request.args.get("value", default=None))
    match search.state:

        case Success():
            return {
                "message":
                    f"Success! Found: {len(search.result)} stores.",
                "stores": search.result
            }

        case NoResults():
            return {
                "message":
                    f"No results received: {search.query}."}

        case ParseFailed():
            return {
                "message": search.result}

        case NoResponse():
            return {
                "message":
                    "API response was empty or invalid."
            }
        case _:
            return {
                "message": "Unknown server error."}


@app.route("/store/query/select/", methods=["GET", "POST"])
def modify_store_queries():
    """Add or remove a store query from user session.

    Which action to take is determined by the method
    used in the request: (POST = ADD GET = REMOVE)

    Adding requires a tuple in the form: (name, id, slug),
    to be present in the request.json["store"] key.

    Removing requires a store id string to be present in
    the request.args["id"] key.
    """
    stores = session.get("stores", default=[])
    if request.method == "POST":
        logger.debug("Adding a store query to stores list...")
        result, stores = add_store_query(
            request_json=request.json,
            stores=stores)
    else:
        logger.debug("Removing a store query from stores list...")
        result, stores = remove_store_query(
            request_args=request.args,
            stores=stores)
    session["stores"] = stores
    return {"result": result}


@app.route("/product/query/", methods=["GET"])
def product_search():
    """Query stores list with stored product queries.

    TODO: rest of this docstring
    """
    if len(stores := session.get("stores", default=[])) == 0:
        return redirect(url_for(".main_page"))
    if len(queries := session.get("queries", default=[])) == 0:
        return redirect(url_for(".main_page"))

    # Expensive operation, Store class will be reworked later
    stores: list[Store] = [Store(x, y, z) for x, y, z in stores]

    results = loop.run_until_complete(
        execute_product_search(queries=queries, stores=stores))
    session["results"] = results
    return {"url": url_for(".results_page")}


@app.route("/product/query/select/", methods=["GET", "POST"])
def modify_product_queries():
    """Add or remove a product query from user session.

    Which action to take is determined by the method
    used in the request: (POST = ADD GET = REMOVE)
    """
    products = session.get("products", default=[])
    if request.method == "POST":
        logger.debug("Adding a product query to products list...")
        result, products = add_product_query(
            request_json=request.json,
            products=products)
        
    else:
        logger.debug("Removing a product query from products list...")
        result, products = remove_product_query(
            request_args=request.args,
            products=products)

    session["products"] = products
    return {"result": result}
