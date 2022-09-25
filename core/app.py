from flask import redirect, url_for, render_template, request
from core import app, validate_post, ProductList, parse_input
from api import get_groceries
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
    request_json = validate_post(request)
    if validate_post(request=request):
        operation = request.json["operation"]
        product_queries = parse_input(request=request)

        if operation == "Groceries":
            logger.info(f"Current operation: {operation}")
            results = asyncio.run(get_groceries(
                request=request,
                product_queries=product_queries,
                limit=24))
            for r in results:
                logger.info(r)
            return {"data": ""}
        else:
            return {"data": "[ERROR]: Operation not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
