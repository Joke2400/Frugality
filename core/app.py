from flask import redirect, url_for, render_template, request, session, flash
from utils import validate_post, get_quantity, get_specifiers, print_results, timer
from core import app, QueryItem, AmountTuple, ProductList
from api import get_groceries
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
        product_queries = []
        for q, a, c in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
            if q == "":
                continue
            a = int(a) if a != "" else 0
            t = AmountTuple(amount=a, **get_quantity(q))
            m = get_specifiers(q)
            product_queries.append(
                QueryItem(
                    name=q,
                    amt=t,
                    category=c,
                    must_contain=m))

        if operation == "Groceries":
            asyncio.run(get_groceries(
                request=request,
                product_queries=product_queries,
                limit=10))

        else:
            return {"data": "[ERROR]: Operation not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
    return {"data": "DONE!"}