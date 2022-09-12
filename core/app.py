from winreg import QueryReflectionKey
from flask import redirect, url_for, render_template, request, session, flash
from api import queries, send_post
from utils import validate_post
from core import app, QueryItem

import json

@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")

@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))

@app.route("/query/", methods=["POST"])
def query():
    if validate_post(request=request):
        operation = request.json["operation"]
        query = request.json["query"].split(") ")
        query = [x.strip("()") for x in query]
        query_items = []
        for i in query:
            x = i.split(",")
            x = [x.strip() for x in x]
            category = None
            if len(x) > 1:
                category = x[1]
            y = x[0].split("[")
            y = [y.strip("]") for y in y]   #Temporary spaghetti code 
            amt = None              #cause im too lazy to learn regex right now
            if len(y) > 1:          #TLDR: Seperates name, amt and category from
                amt = y[1]          #following string format:          
            name = y[0].strip()     #(name [amt], category) (name [amt], category) etc
            query_items.append(     #where both amt and category are optional params
                QueryItem(
                    name,
                    amt,
                    category

                ))
        print(f"Current operation: {operation}")
        print(query_items)

        if operation == "Groceries":
            operation = "GetProductByName"
            query = queries[operation]
            
            for i in query_items:
                variables = {
                    "StoreID": request.json["store_id"],
                    "limit": 10
                    }
                variables["query"] = i.query
                if i.amt is not None:
                    variables["query"] = i.query + " " + i.amt
                variables["slugs"] = i.category if i.category is not None else ""
                response = send_post(
                    query=query,
                    operation_name=operation,
                    variables=variables
                )
                response_json = json.loads(response.text)
                items = response_json["data"]["store"]["products"]["items"]
                max_priced_item = max(items, key=lambda x: x["comparisonPrice"])
                min_priced_item = min(items, key=lambda x: x["comparisonPrice"])
                print(f"\nQuery: {variables['query']}")
                print(f"Cheapest: {min_priced_item['name']} {min_priced_item['comparisonPrice']}€/{min_priced_item['comparisonUnit']}")
                print(f"Most expensive: {max_priced_item['name']} {max_priced_item['comparisonPrice']}€/{min_priced_item['comparisonUnit']}")
            return {"data": "DONE!"}
    return {"data": "[ERROR]: Validation failed, JSON is missing"}