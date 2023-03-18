from flask import redirect, url_for, render_template, request, session
from core import (
    app,
    execute_product_search,
    parse_store_from_string,
    parse_query_data,
    execute_store_search
)
from utils import LoggerManager as lgm
import re

logger = lgm.get_logger(name=__name__)


@app.route("/", methods=["GET"])
def main():
    queries = session.get("queries", default=[])
    products = session.get("products", default=[])
    stores = session.get("stores", default=[])
    store_names = []
    if len(stores) > 0:
        for i in stores:
            store_names.append(i[0])
    return render_template(
        "search.html",
        queries=queries,
        products=products,
        store_names=store_names)


@app.route("/query/", methods=["GET"])
def query():
    if (store := session.get("store")):
        if queries := session.get("queries"):
            product_lists = execute_product_search(
                query_data=queries,
                store=store,
                limit=20)
            products = []
            for i in product_lists:
                if (cheapest := i.cheapest_item) is not None:
                    products.append(cheapest.dictify())
            session["products"] = products
            return {"products": products}
    return redirect(url_for("main"))


@app.route("/add_store/", methods=["POST"])
def add_store():
    try:
        store_query = re.sub(
            pattern=r"[^a-zA-Z0-9\såäö-]",
            repl="",
            string=str(request.json["store"]),
            flags=re.I | re.M)
    except (TypeError, ValueError) as err:
        logger.exception(err)
        return redirect(url_for("main"))

    if store_query not in ("", None):
        parsed_data = parse_store_from_string(string=store_query)
        if any(parsed_data):
            store_data = execute_store_search(query_data=parsed_data)
            if not store_data:
                logger.debug("Could not find the queried store.")
                return redirect(url_for("main"))

            stores = session.get("stores", default=[])
            if store_data not in stores:
                stores.append(store_data)
                logger.debug("Added %s into stores", store_data)
            session["stores"] = stores
    return {"stores": stores}


@app.route("/remove_store/", methods=["POST"])
def remove_store():
    try:
        index = int(request.json["index"])
    except (KeyError, ValueError) as err:
        logger.exception(err)
        return redirect(url_for)
    stores = session.get("stores", default=[])
    item = stores[index]
    stores.remove(item)
    session["stores"] = stores
    return {"stores": stores}


@app.route("/add_query/", methods=["POST"])
def add_query():
    queries = session.get("queries", default=[])
    if (query_dict := parse_query_data(request.json)):
        in_list = False
        for i in queries:
            if query_dict["slug"] == i["slug"]:
                in_list = True
                i["count"] += query_dict["count"]
                logger.debug("Added '%s' to count of: '%s'.",
                             query_dict["count"], i["query"])
                break
        if not in_list:
            queries.append(query_dict)
            logger.debug("Added new query: '%s' to list.",
                         query_dict["query"])
    session["queries"] = queries
    return {"queries": queries}


@app.route("/remove_query/", methods=["POST"])
def remove_query():
    try:
        index = int(request.json["index"])
    except (KeyError, ValueError) as err:
        logger.exception(err)
        return redirect(url_for)
    queries = session.get("queries", default=[])
    item = queries[index]
    if item["count"] > 1:
        item["count"] -= 1
    else:
        queries.remove(item)
    session["queries"] = queries
    return {"queries": queries}
