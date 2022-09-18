from flask import redirect, url_for, render_template, request
from core import app, validate_post, ProductList
from utils import timer

import asyncio
import api


@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")


@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))


@app.route("/query/", methods=["POST"])
@timer
def query():
    if validate_post(request=request):
        operation = request.json["operation"]
        print(f"\nCurrent operation: {operation}")
        product_queries = api.parse_input(request=request)

        ProductList.reset_total_cost()
        if operation == "Groceries":
            results = asyncio.run(api.get_groceries(
                request=request,
                product_queries=product_queries,
                limit=24))
            for r in results:
                print(r)
            return {"data": {
                "total_cheap": f"{ProductList.total_cheap:.2f}",
                "total_expensive": f"{ProductList.total_expensive:.2f}",
                "total_avg": f"{ProductList.total_avg:.2f}"}}
        else:
            return {"data": "[ERROR]: Operation not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
