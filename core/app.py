from flask import redirect, url_for, render_template, request, session, flash
from utils import validate_post, get_quantity, get_specifiers, timer
from core import app, QueryItem, AmountTuple
from api import get_groceries, parse_input
import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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
        product_queries = parse_input(request=request)

        if operation == "Groceries":
            results = asyncio.run(get_groceries(
                request=request,
                product_queries=product_queries,
                limit=24))
            for r in results:
                print(r)

        else:
            return {"data": "[ERROR]: Operation not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
    return {"data": "DONE!"}