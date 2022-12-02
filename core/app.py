from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    validate_post,
    parse_input,
    extract_request_json,
    parse_store_input,
    execute_product_search,
    get_store_data,
    validate_store_data,
    products_overview
)
from utils import timer, LoggerManager as lgm
import re

logger = lgm.get_logger(name=__name__)


@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")


@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))


@app.route("/set_store/", methods=["POST"])
def set_store():
    # NEEDS TO BE SANITIZED?
    store = request.json["store"]
    s = re.match(pattern=r"[a-zA-Z]+|\d+|\s+",
                 string=store,
                 flags=re.I | re.M)
    if s is None:
        return {"data": "Could not set store"}
    store = s.string
    if store != session.get("store") and store not in ("", None):
        session["store"] = str(store)
        logger.debug(f"Set '{session['store']}' as session store.\n")
    return {"data": store}


@app.route("/query/", methods=["POST"])
@timer
def query():
    # TODO: Add handling for error response codes
    logger.info("Received a new product query!\n")
    if not validate_post(request):
        return {"data": "[ERROR]: Request validation failed."}

    # Get store and/or id from user session
    if session.get("store") not in ("", None):
        logger.debug(f"Store '{session['store']}' found in session.\n")
        store_data = parse_store_input(store_str=session["store"])
    else:
        # Temporary
        # Should just prompt the user for re-input here
        logger.info("No store was set for active session\n")
        return {"data": "Store must be set."}

    # Get store data from api
    response = get_store_data(store_data=store_data)
    # Validate that user input present in request
    store_data = validate_store_data(response=response,
                                     store_data=store_data)
    if store_data is None:
        # Temporary, either search for store here using gmaps, or scraping
        # The smarter thing to do however, would be to just prompt
        # the user for re-input
        return {"data": "Could not find store"}

    # Get request field dicts in a tuple
    request_data = extract_request_json(request=request)
    # Get list of QueryItems
    query_data = parse_input(data=request_data, store=store_data)
    session["queries"] = query_data

    # Get a list containing ProductList(s)
    product_lists = execute_product_search(
        query_data=query_data,
        store_id=store_data[1],
        limit=20)
    # Only printing for now ->
    products_overview(product_lists)

    return {"data": "Success!"}
