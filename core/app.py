"""Main file for Flask app, contains all the app routes."""

import asyncio
from flask import redirect, url_for, render_template
from flask import request, session, Blueprint

from utils import LoggerManager

from .store_flow import execute_store_search
from .store import Store, Found, NotFound, ParseFailed
from .product_flow import execute_product_search
from .product_flow import parse_user_query


logger = LoggerManager.get_logger(name=__name__)
app = Blueprint(name="Frugality", import_name=__name__)
loop = asyncio.get_event_loop()


@app.route("/", methods=["GET"])
def main():
    """Return a template for the main page."""
    queries = session.get("queries", default=[])
    products = session.get("products", default=[])
    stores = session.get("stores", default=[])
    store_names = []
    if len(stores) > 0:
        for i in stores:
            store_names.append(i[0])
    return render_template(
        "index.html",
        queries=queries,
        products=products,
        store_names=store_names)


@app.route("/add_store/", methods=["POST"])
def add_store():
    """Append a store to the user session stores list.

    Execute search on string provided in request JSON.
    Query results are then interpreted and the store is
    added to session if query was successful.

    Returns:
        dict: Returns a dict with a key 'stores' containing
            current stores in user session. Dict also contains
            a 'message' key which gives results feedback to the end-user.
    """
    store: Store = execute_store_search(string=request.json["store"])
    match store.state:

        case Found():
            stores = session.get("stores", default=[])
            if (data := store.data) not in stores:
                stores.append(data)
                logger.debug("Added %s into session stores.", data)
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
    """Remove a store from the (session) store list.

    Takes in an index (int) as a JSON key.
    The index is used to remove the store from the list.

    Returns:
        Dict with a single key-value pair. Value of returned
        dict key is a list of stores in user session.
    """
    try:
        index = int(request.json["index"])
    except (KeyError, ValueError) as err:
        logger.exception(err)
        return {"stores": session.get("stores", default=[])}
    stores = session.get("stores", default=[])
    item = stores[index]
    stores.remove(item)
    session["stores"] = stores
    return {"stores": stores}


@app.route("/product_query/", methods=["GET"])
def product_query():
    """Query stores list with stored product queries.

    TODO: rest of this docstring
    """
    if len(stores := session.get("stores", default=[])) == 0:
        return redirect(url_for("main"))
    if len(queries := session.get("queries", default=[])) == 0:
        return redirect(url_for("main"))

    # Expensive operation, Store class will be reworked later
    stores: list[Store] = [Store(x, y, z, Found()) for x, y, z in stores]

    results = loop.run_until_complete(
        execute_product_search(queries=queries, stores=stores))
    return {"TEST": "TEST"}
    for store in results:
        for i in store[1]:
            print(i.products)
    return render_template(
        "products.html",
        results=results)


@app.route("/add_query/", methods=["POST"])
def add_query():
    """Add a query to the (session) query list.

    Takes in a JSON dict.
    Given dict gets parsed and added to queries if an
    identical query does not already exist in list.
    If this is the case, the 'count' variables of both
    queries get added together.

    Returns:
        Dict with a single key-value pair. Value of returned
        dict key is a list of queries in user session.
    """
    queries = session.get("queries", default=[])
    if (query_dict := parse_user_query(request.json)):
        in_list = False
        for i in queries:
            if query_dict["slug"] == i["slug"]:
                in_list = True
                i["count"] += query_dict["count"]
                logger.debug("Added '%s' to count of: '%s'.",
                             query_dict["count"], i["query"])
                break
        if not in_list:
            queries.append(query_dict)
            logger.debug("Added new query: '%s' to list.",
                         query_dict["query"])
    session["queries"] = queries
    return {"queries": queries}


@app.route("/remove_query/", methods=["POST"])
def remove_query():
    """Remove a query from the (session) query list.

    Takes in an index (int) as a JSON key.
    The index is used to remove the query from the list.

    Returns:
        Dict with a single key-value pair. Value of returned
        dict key is a list of queries in user session.
    """
    try:
        index = int(request.json["index"])
    except (KeyError, ValueError) as err:
        logger.exception(err)
        return redirect(url_for)
    queries = session.get("queries", default=[])
    if len(queries) == 0:
        return {"queries": queries}
    try:
        item = queries[index]
    except IndexError:
        logger.debug(
            "Could not manipulate item @ index: %s", index)
        return {"queries": queries}
    if item["count"] > 1:
        item["count"] -= 1
    else:
        queries.remove(item)
    session["queries"] = queries
    return {"queries": queries}
