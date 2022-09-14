from typing import NamedTuple
from flask import redirect, url_for, render_template, request, session, flash
from api import queries, send_post
from utils import validate_post
from core import app, QueryItem, ResultItem

import json
import re

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
        print(f"\nCurrent operation: {operation}")
        patterns = ["(\d+)(l|k?gm?)", "laktoositon"]
        for q, a, c in zip(
            request.json["queries"],
            request.json["amounts"],
            request.json["categories"]):
            m = []
            for p in patterns:
                m.append(re.findall(
                pattern=p, 
                string=q,
                flags=re.I|re.M))
            QueryItem(
                name=q,
                amt=a,
                category=c,
                must_contain=m)
        """
        if operation == "Groceries":
            query_operation = "GetProductByName"
            query = queries[operation]
            
            avg_prices = []
            min_prices = []
            max_prices = []
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
                items = [ResultItem(
                    name=i["name"],
                    ean=i["ean"],
                    price=i["price"],
                    basic_quantity_unit=i["basicQuantityUnit"],
                    comparison_price=i["comparisonPrice"],
                    comparison_unit=i["comparisonUnit"]
                ) for i in items]
                max_priced_item = max(items, key=lambda x: x.comparison_price)
                min_priced_item = min(items, key=lambda x: x.comparison_price)
                avg_priced_item = sum(i.comparison_price for i in items) / len(items)
                min_prices.append(min_priced_item.comparison_price)
                max_prices.append(max_priced_item.comparison_price)
                avg_prices.append(avg_priced_item)
                print(f"\nQuery: {variables['query']}, Category: {variables['slugs']}\n")
                print(f"Cheapest: {'': ^20}{min_priced_item.comparison_price:.2f}{'':<2}€/{min_priced_item.comparison_unit}{'':^7}{min_priced_item.name}")
                print(f"Most expensive: {'': ^14}{max_priced_item.comparison_price:.2f}{'':<2}€/{min_priced_item.comparison_unit}{'':^7}{max_priced_item.name}")
                print(f"Average price: {'': ^15}{avg_priced_item:.2f}{'':<2}€/{min_priced_item.comparison_unit}")

            print("\n")
            print(f"Min: {'': ^25}{sum(min_prices):.2f}€")
            print(f"Max: {'': ^25}{sum(max_prices):.2f}€")
            print(f"Avg: {'': ^25}{sum(avg_prices):.2f}€")
            print("")

            #TODO: Check that string contain a certain word, ex searching currently hillosokeri also yields all produkts with just sokeri

            return {"data": "DONE!"}
        """
    return {"data": "[ERROR]: Validation failed, JSON is missing"}