from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    process_queries,
    execute_product_search,
    parse_store_from_string,
    parse_query_data,
    execute_store_search
)
from utils import LoggerManager as lgm
import re

logger = lgm.get_logger(name=__name__)


@app.route("/", methods=["GET"])
def main():
    queries = session.get("queries", default=[])
    products = session.get("products", default=[])
    if (store := session.get("store")):
        store = store[0]
    else:
        store = "No store selected"
    return render_template(
        "index.html",
        queries=queries,
        products=products,
        store=store
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
        return redirect(url_for("main"))
    parsed_data = parse_store_from_string(string=store_query)
    if not any(parsed_data):
        return redirect(url_for("main"))
    if (store := session.get("store")) and parsed_data[0] is not None:
        if store[0].lower() == parsed_data[0].lower():
            logger.debug(
                "Store query was equal to session store, aborting query...")
            return redirect(url_for("main"))
    store_data = execute_store_search(query_data=parsed_data)
    if not store_data:
        logger.debug("Returned store data was empty, returning 'not found'.")
        return redirect(url_for("main"))
    session["store"] = store_data
    logger.debug("Set %s as session store.", store_data)
    return redirect(url_for("main"))


@app.route("/query/", methods=["POST"])
def query():
    if (store := session.get("store")):
        if (query_data := process_queries(data=request.json)):
            product_lists = execute_product_search(
                query_data=query_data,
                store=store,
                limit=20)
            session["products"] = product_lists
    return redirect(url_for("main"))


@app.route("/add_query/", methods=["POST"])
def add_query():
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
