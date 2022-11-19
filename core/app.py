from flask import redirect, url_for, render_template, request
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


@app.route("/set_store/")
def set_store():
    pass


@app.route("/query/", methods=["POST"])
@timer
def query():
    logger.info("Received a new request!\n")
    if validate_post(request):
        # Get store name/id
        store_data = parse_store_data(store_str=request.json.pop("store"))
        # Validate
        store_data = validate_store_data(store_data=store_data)

        # Get request field dicts in a tuple
        request_data = extract_request_json(request=request)
        # Get list of QueryItems
        query_data = parse_input(data=request_data, store=store_data)

        # Get a list containing ProductList(s)
        product_lists = execute_product_search(
            query_data=query_data,
            store_id=store_data[1],
            limit=20)
        # Only printing for now ->
        products_overview(product_lists)

        return {"data": ""}
    else:
        return {"data": "[ERROR]: Request validation failed."}
