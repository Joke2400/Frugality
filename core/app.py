from flask import redirect, url_for, render_template, request, session, flash
from utils import validate_post, get_quantity, get_specifiers, get_groceries, print_results
from core import app, QueryItem, AmountTuple, ProductList

@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")

@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))

@app.route("/query/", methods=["POST"])
def query():
    # TODO: Input sanitization will happen in validate_post(), 
    # Flask I think has some funcs for that, 
    # must be done before this gets hosted anywhere
    if validate_post(request=request):
        operation = request.json["operation"]
        print(f"\nCurrent operation: {operation}")
        product_queries = []
        for q, a, c in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
            t = AmountTuple(amount=int(a), **get_quantity(q))
            m = get_specifiers(q)
            product_queries.append(
                QueryItem(
                    name=q,
                    amt=t,
                    category=c,
                    must_contain=m))

        if operation == "Groceries":
            results = [ProductList(r,q,c) for r,q,c in get_groceries(
                request=request,
                product_queries=product_queries,
                limit=10)]
            print_results(results)
        else:
            return {"data": "[ERROR]: Operation not found."}
    else:
        return {"data": "[ERROR]: Request validation failed."}
    return {"data": "DONE!"}