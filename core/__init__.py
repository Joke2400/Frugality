from flask import Flask, redirect, url_for, render_template
from flask_cors import CORS as cors

app = Flask(__name__)
cors(app)

# app URL routing
@app.route("/main/")
def main():
    return "<h1>Main page.</h1>"


@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))