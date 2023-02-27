from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    parse_input,
    extract_request_json,
    execute_product_search,
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
            "category": "Lihat ja kasviproteiinit"
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
    store_query = re.match(pattern=r"[a-zA-Z]+|\d+|\s+",
                           string=str(request.args["query"]),
                           flags=re.I | re.M)
    if store_query in (None, ""):
        logger.debug("Store query was empty, aborting query...")
        return redirect(url_for(message="Store name cannot be empty.",
                                endpoint="main"))
    if store := session.get("store"):
        if store[0].lower() == store_query.string.lower():
            logger.debug(
                "Store query was equal to session store, aborting query...")
            return redirect(url_for(endpoint="main"))

    store_data = execute_store_search(string=store_query.string)
    if not store_data:
        logger.debug("Returned store data was empty, returning 'not found'.")
        return redirect(url_for(message="Store not found.",
                                endpoint="main"))
    session["store"] = store_data
    logger.debug("Set %s as session store.", store_data)
    return redirect(url_for(endpoint="main"))


@app.route("/query/", methods=["POST"])
@timer
def query():
    logger.info("Received a new product query!\n")
    # Get request field dicts in a tuple
    request_data = extract_request_json(request=request)
    # Get list of QueryItemss
    query_data = parse_input(data=request_data, store=store_data)
    session["queries"] = query_data

    # Get a list containing ProductList(s)
    product_lists = execute_product_search(
        query_data=query_data,
        store_id=store_data[1],
        limit=20)
    
    for x in product_lists:
        pass
    
    return render_template("index.html")

