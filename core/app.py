from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    validate_post,
    parse_input,
    extract_request_json,
    parse_store_data,
    execute_product_search,
    validate_store_data,
    products_overview
)
from utils import timer, LoggerManager as lgm

logger = lgm.get_logger(name=__name__)


@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")


@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))


@app.route("/set_store/", methods=["POST"])
def set_store():
    # NEEDS TO BE SANITIZED
    store = request.json["store"]
    if store != session.get("store"):
        session["store"] = store
        logger.debug(f"Set '{session['store']}' as session store.\n")
    return {"data": store}


@app.route("/query/", methods=["POST"])
@timer
def query():
    logger.info("Received a new product query!\n")
    if validate_post(request):
        # Get store name/id
        if session.get("store") is not None:
            logger.debug(f"Store '{session['store']}' found in session.\n")
            store_data = parse_store_data(store_str=session["store"])
        else:
            logger.info("No store was set for active session!\n")
            return {"data": "Store must be set."}
        # Validate
        store_data = validate_store_data(store_data=store_data,
                                         requested=session["store"])

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
    else:
        return {"data": "[ERROR]: Request validation failed."}
