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
    session_store = session.get("store")
    if session_store:
        session_store = session_store[0]
    message = request.args.get("message")
    if not message:
        message = ""
    session_queries = session.get("queries")
    if not session_queries:
        # Temporary
        session_queries = [{
            "name": "Maito Laktoositon 1L",
            "amount": 2,
            "category": "Maito, munat ja rasvat"
        },
        {
            "name": "Naudan Jauheliha 400g",
            "amount": 1,
            "category": ""
        },
        {
            "name": "Chiquita Banaani",
            "amount": 3,
            "category": "Hedelmät ja Vihannekset"
        }]
    return render_template("index.html", message=message,
                           session_store=session_store,
                           session_queries=session_queries)


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
        return redirect(url_for(message="Store name cannot be empty.",
                                endpoint="main"))
    parsed_data = parse_store_from_string(string=store_query)
    if not any(parsed_data):
        return redirect(url_for(message="ERROR when parsing store.",
                                endpoint="main"))
    if (store := session.get("store")) and parsed_data[0] is not None:
        if store[0].lower() == parsed_data[0].lower():
            logger.debug(
                "Store query was equal to session store, aborting query...")
            return redirect(url_for(endpoint="main"))
    store_data = execute_store_search(query_data=parsed_data)
    if not store_data:
        logger.debug("Returned store data was empty, returning 'not found'.")
        return redirect(url_for(message="Store not found.",
                                endpoint="main"))
    session["store"] = store_data
    logger.debug("Set %s as session store.", store_data)
    return redirect(url_for(endpoint="main"))


@app.route("/query/", methods=["POST"])
def query():
    logger.info("Received a new product query!\n")
    if not (store := session.get("store")):
        return redirect(url_for(endpoint="main"))

    if not (query_data := process_queries(json=request.json, store=store)):
        return redirect(url_for(endpoint="main"))
    session["queries"] = query_data
    product_lists = execute_product_search(
        query_data=query_data,
        store=store,
        limit=20)
    print(product_lists)
    return render_template("index.html")

