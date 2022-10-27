from flask import redirect, url_for, render_template, request
from core import app, validate_post, parse_input, extract_request_json
from api import get_products
from core.app_funcs import parse_response
from utils import timer, LoggerManager as lgm

import asyncio

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
    if validate_post(request):
        operation = request.json.pop("operation")
        store_id = request.json.pop("store_id")
        data = extract_request_json(request)

        product_queries = parse_input(data)

        # Simple check, needs to be improved later
        if operation == "Groceries":
            logger.info(f"\nCurrent operation: {operation}\n")
            responses = asyncio.run(get_products(
                store_id=store_id,
                product_queries=product_queries,
                limit=10))

            product_lists = []
            for r in responses:
                product_lists.append(parse_response(*r))

            for pl in product_lists:
                logger.info(f"Products found: {len(pl.products)}")
                logger.info(f"Filtered products: {len(pl.filtered_products)}")
                logger.info(pl.get_products_overview(filtered=True))
                for y in pl.filtered_products:
                    logger.info(f"\n{'-'*50}{y}{'-'*50}\n")

            return {"data": ""}
        else:
            return {"data": f"[ERROR]: Operation '{operation}' not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
