from flask import redirect, url_for, render_template, request
from core import app, validate_post, parse_input, extract_request_json, create_product_list, parse_store_info
from api import get_products
from utils import timer, LoggerManager as lgm

import asyncio
import json

logger = lgm.get_logger(name=__name__)


@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")


@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))


@app.route("/query/", methods=["POST"])
@timer
def query():
    logger.info("Received a new request!\n")
    if validate_post(request):
        operation = request.json.pop("operation")
        store_str = request.json.pop("store")

        store_data = parse_store_info(store_str)
        if store_data is None:
            return {"data": "[ERROR]: Store name or id must be specified."}

        request_data = extract_request_json(request)
        query_data = parse_input(request_data, store_data)

        # Simple check, needs to be improved later
        if operation == "Groceries":
            logger.info(f"Current operation: {operation}\n")
            responses = asyncio.run(get_products(
                store_id=store_data[1],
                product_queries=query_data,
                limit=10))

            product_lists = []
            for r in responses:
                product_lists.append(create_product_list(*r))

            for pl in product_lists:
                p_len = len(pl.products)
                logger.info(f"Products found: {p_len}.")
                f_str = pl.query.amount.quantity  # Maybe set filter to this value as default, then add a apply filter func

                if f_str not in (None, ""):
                    pl.set_filter(f_str)
                    f_len = len(pl.products)
                    logger.info(
                        f"Excluding products that do not contain: '{f_str}'.")
                    logger.info(f"Filtered out {p_len - f_len} products. " +
                                f"Remaining products: {f_len}.")
                logger.info(pl)

            return {"data": ""}
        else:
            return {"data": f"[ERROR]: Operation '{operation}' not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
