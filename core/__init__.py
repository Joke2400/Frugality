from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "test"
app.permanent_session_lifetime = timedelta(days=1)

# app URL routing
@app.route("/main/")
def main():
    return render_template("index.html")

@app.route("/")
def base_url_redirect():
    return redirect(url_for("main"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["name"]
        session["user"] = user
        flash("Login successful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/logout/")
def logout():
    flash("Logout successful", "info")
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/user/")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))

