from flask import redirect, url_for, render_template, request, session, flash, jsonify
from core import app
import json

from api import queries, send_post

@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")

@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))

@app.route("/recipes")
@app.route("/recipes/")
def recipes():
    return render_template("recipes.html")

@app.route("/query/", methods=["POST"])
def query():
    if request.method == "POST":
        print(f"Operation: {operation} ({type(operation)})")
        operation = request.json["operation"] if not None else ""
    
        if operation in queries:
            query = queries[operation]
            variables = json.loads(variables)
            response = send_post(query, operation, variables)
        return {"data": response.text}


@app.route("/recipes/fetch")
@app.route("/recipes/fetch/")
def recipe_fetch():
    return {"data": (
        {"name": "Chicken and rice"},
        {"name": "Noodles"},
        {"name": "Tomato soup"},
        {"name": "Banana split"},
        {"name": "Pepperoni Pizza"},
        {"name": "Pea soup"},
        {"name": "Meatballs"},
        )}