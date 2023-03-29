"""Main file for Flask app, contains all the app routes."""

import asyncio
from flask import redirect, url_for, render_template
from flask import request, session, Blueprint

from utils import LoggerManager

from .orm import DataManager as Manager
from .orm import Store
from .app_funcs import execute_store_search
from .app_funcs import execute_store_product_search
from .app_funcs import validate_store_query
from .app_funcs import parse_store_from_string
from .app_funcs import parse_query_data


logger = LoggerManager.get_logger(name=__name__)
app = Blueprint(name="Frugality", import_name=__name__)


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
    """Add a store to the (session) store list.

    Takes in a string as a JSON key.
    Given string gets parsed, queried and then validated
    before being added to stores list if not already present.
    If store does not exist in database, add it.

    Returns:
        Dict with a single key-value pair. Value of returned
        dict key is a list of stores in user session.
    """
    if (store_query := validate_store_query(
            request.json["store"])) is None:
        return {"stores": session.get("stores", default=[])}

    parsed_data = parse_store_from_string(store_query)
    if not any(parsed_data):
        logger.debug("Could not parse store from string.")
        return {"stores": session.get("stores", default=[])}
    value = {
        "store_id": parsed_data[1]} if parsed_data[1] else {
        "slug": parsed_data[2]}
    results = Manager.filtered_query(Store, **value).all()

    if len(results) == 0:
        store_data = execute_store_search(parsed_data=parsed_data)
        if not store_data:
            logger.debug("Could not find the queried store.")
            return {"stores": session.get("stores", default=[])}
        Manager.add_store_record(data=store_data)
    else:
        store_data = (results[0].name,
                      results[0].store_id,
                      results[0].slug)
    stores = session.get("stores", default=[])
    if store_data not in stores:
        stores.append(store_data)
        logger.debug("Added %s into stores", store_data)
    session["stores"] = stores
    return {"stores": stores}


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
async def product_query():
    """Query stores list with stored product queries.

    TODO: rest of this docstring
    """
    if len(stores := session.get("stores", default=[])) == 0:
        return redirect(url_for("main"))
    if len(queries := session.get("queries", default=[])) == 0:
        return redirect(url_for("main"))
    results = await execute_store_product_search(
        queries=queries,
        stores=stores)
    """
    for store in results:
        for store, product_queries in store.items():
            logger.info("Store: %s", store)
            for product_list in product_queries:
                logger.info(
                    "Cheapest item: %s", product_list.cheapest_item)
    """
    return {"NOT_IMPLEMENTED": "NOT_IMPLEMENTED"}


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
    if (query_dict := parse_query_data(request.json)):
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
    item = queries[index]
    if item["count"] > 1:
        item["count"] -= 1
    else:
        queries.remove(item)
    session["queries"] = queries
    return {"queries": queries}
