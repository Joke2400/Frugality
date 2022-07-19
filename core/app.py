from flask import redirect, url_for, render_template, request, session, flash, jsonify
from core import app
import json

from api import queries, send_post

@app.route("/main/", methods=["POST", "GET"])
def main():
    return render_template("index.html")

@app.route("/query/", methods=["POST"])
def query():
    if request.method == "POST":
        operation = request.json["operation"]
        variables = request.json["variables"]
        print(f"Operation: {operation} ({type(operation)})")
        print(f"Operation: {variables} ({type(variables)})")
        if operation in queries:
            query = queries[operation]
            variables = json.loads(variables)
            response = send_post(query, operation, variables)
        return {"data": response.text}

@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))
