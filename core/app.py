from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    process_queries,
    execute_product_search,
    parse_store_from_string,
    execute_store_search
)
from utils import timer, LoggerManager as lgm
import re

logger = lgm.get_logger(name=__name__)


@app.route("/", methods=["GET"])
def main():
    if len(session_queries := session.get("queries", default=[])) != 0:
        queries = []
        for i in session_queries:
            queries.append({
                "name": i.name,
                "count": i.count,
                "quantity": i.quantity,
                "unit": i.unit,
                "category": i.category
            })
        session_queries = queries
    if len(session_products := session.get("products", default=[])) != 0:
        products = []
        for i in session_products:
            products.append({
                "name": i.name,
                "count": i.count,
                "category": i.category,
                "ean": i.ean,
                "comparison_unit": i.comparison_unit,
                "comparison_price": i.comparison_price,
                "unit_price": i.unit_price,
                "label_quantity": i.label_quantity,
                "label_unit": i.label_unit
            })
        session_products = products
    if not (message_state := session.get("message_state")):
        message_state = "No current message."
    if (session_store := session.get("store")):
        store_state = session_store[0]
    else:
        store_state = "No store selected"
    return render_template(
        "index.html",
        message_state=message_state,
        store_state=store_state,
        session_store=session_store,
        session_products=session_products,
        session_queries=session_queries,
        queries_state=f"Queries length: {len(session_queries)}",
        products_state=f"Products length: {len(session_products)}"
    )


@app.route("/get_store/", methods=["GET"])
def get_store():
    """Endpoint to fetch a store from the API using a query string.

    If a store is found, save it in the user session. Otherwise relay a
    feedback message to the end user via the 'message' argument to url_for
    when redirecting back to the main page.

    Returns:
        Response: Returns a redirect main page url.
    """
    logger.debug("Store query received!")
    store_query = re.sub(pattern=r"[^a-zA-Z0-9\s]",
                         repl="",
                         string=str(request.args["query"]),
                         flags=re.I | re.M)
    if store_query in (None, ""):
        logger.debug("Store query was empty, aborting query...")
        session["message_state"] = "Store name cannot be empty."
        return redirect(url_for("main"))
    parsed_data = parse_store_from_string(string=store_query)
    if not any(parsed_data):
        session["message_state"] = "Error parsing store."
        return redirect(url_for("main"))
    if (store := session.get("store")) and parsed_data[0] is not None:
        if store[0].lower() == parsed_data[0].lower():
            logger.debug(
                "Store query was equal to session store, aborting query...")
            return redirect(url_for("main"))
    store_data = execute_store_search(query_data=parsed_data)
    if not store_data:
        logger.debug("Returned store data was empty, returning 'not found'.")
        session["message_state"] = "Store was not found."
        return redirect(url_for("main"))
    session["store"] = store_data
    logger.debug("Set %s as session store.", store_data)
    session["message_state"] = "Set new session store."
    return redirect(url_for("main"))


@app.route("/query/", methods=["POST"])
def query():
    logger.info("Received a new product query!\n")
    if not (store := session.get("store")):
        return redirect(url_for("main"))

    if not (query_data := process_queries(data=request.json)):
        return redirect(url_for("main"))
    session["queries"] = query_data
    product_lists = execute_product_search(
        query_data=query_data,
        store=store,
        limit=20)
    session["products"] = product_lists
    session["message_state"] = "Product search successful."
    return redirect(url_for("main"))
