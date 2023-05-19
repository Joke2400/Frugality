"""Main file for Flask app, contains all the app routes."""

import asyncio
from flask import redirect, url_for, render_template
from flask import request, session, Blueprint

from utils import LoggerManager

from .store_flow import execute_store_search
from .store_flow import remove_store_query
from .store import Store, Found, NotFound, ParseFailed
from .product_flow import execute_product_search
from .product_flow import remove_product_query
from .product_flow import add_product_query


logger = LoggerManager.get_logger(name=__name__)
app = Blueprint(name="Frugality", import_name=__name__)
loop = asyncio.get_event_loop()


@app.route("/", methods=["GET"])
def main_page():
    """Return a template for the main page."""
    queries = session.get("queries", default=[])
    stores = session.get("stores", default=[])
    store_names = []
    if len(stores) > 0:
        for i in stores:
            store_names.append(i[0])
    return render_template(
        "index.html",
        queries=queries,
        store_names=store_names)


@app.route("/results/", methods=["GET"])
def results_page():
    """Return a template for the results page."""
    results = session.get("results", default=[])
    return render_template(
        "results.html",
        results=results)


@app.route("/store/query/", methods=["GET"])
def query():
    return {
        "result": ("Prisma Olari", "542862479", "prisma-olari")}


@app.route("/add_store/", methods=["POST"])
def add_store():
    """Append a store to the user session stores list.

    Execute search on string provided in request JSON.
    Query results are then interpreted and the store is
    added to session if query was successful.
    """
    store: Store = execute_store_search(string=request.json["store"])
    match store.state:

        case Found():
            stores = session.get("stores", default=[])
            if (data := store.data) not in stores:
                stores.append(data)
                logger.debug("Added %s into session.", data)
            session["stores"] = stores
            return {"stores": stores,
                    "message": "SUCCESS!"}

        case NotFound():
            return {
                "stores": session.get("stores", default=[]),
                "message": "STORE NOT FOUND"}

        case ParseFailed():
            return {
                "stores": session.get("stores", default=[]),
                "message": "PARSE ERROR"}

        case _:
            return {
                "stores": session.get("stores", default=[]),
                "message": "UNKNOWN SERVER ERROR"}


@app.route("/remove_store/", methods=["POST"])
def remove_store():
    """Remove a store from the (session) store list."""
    stores = remove_store_query(stores=session.get("stores", default=[]),
                                request_json=request.json)
    session["stores"] = stores
    return {"stores": stores}


@app.route("/add_query/", methods=["POST"])
def add_query():
    """Add a query to the (session) query list."""
    queries = add_product_query(queries=session.get("queries", default=[]),
                                request_json=request.json)
    session["queries"] = queries
    return {"queries": queries}


@app.route("/remove_query/", methods=["POST"])
def remove_query():
    """Remove a query from the (session) query list."""
    queries = remove_product_query(queries=session.get("queries", default=[]),
                                   request_json=request.json)
    session["queries"] = queries
    return {"queries": queries}


@app.route("/product_search/", methods=["GET"])
def product_search():
    """Query stores list with stored product queries.

    TODO: rest of this docstring
    """
    if len(stores := session.get("stores", default=[])) == 0:
        return redirect(url_for(".main_page"))
    if len(queries := session.get("queries", default=[])) == 0:
        return redirect(url_for(".main_page"))

    # Expensive operation, Store class will be reworked later
    stores: list[Store] = [Store(x, y, z, Found()) for x, y, z in stores]

    results = loop.run_until_complete(
        execute_product_search(queries=queries, stores=stores))
    session["results"] = results
    return {"url": url_for(".results_page")}
