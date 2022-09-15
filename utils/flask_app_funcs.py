from api import queries, send_post
import re

from core.app_dataclasses import ProductList

def basic_regex(p, s):
    return re.findall(
        pattern=p, 
        string=s,
        flags=re.I|re.M)

def validate_post(request):
    if request.method == "POST":
        if request.json is None:
            return False
    return True

def get_quantity(s):
    r = basic_regex("(\d+)(l|k?gm?)", s)
    if len(r) == 0:
        return {"quantity": None, "unit": None}
    r = r[0]
    return {
        "quantity": int(r[0]) if r[0] != "" else None,
        "unit":     r[1] if r[1] != "" else None}

def get_specifiers(s):
    return basic_regex("laktoositon", s)

def get_groceries(request, product_queries, limit=24):
    operation = "GetProductByName"
    query = queries[operation]
    base_variables = {
        "StoreID": request.json["store_id"],
        "limit": limit}

    for i in product_queries:
        variables = base_variables
        variables["query"] = i.name
        variables["slugs"] = i.category
        response = send_post(
            query=query,
            operation_name=operation,
            variables=variables)
        # TODO: Check that string contain string in QueryItem.must_contain
        yield response, i.name, i.category

def print_results(results):
    for r in results:
        print(f"\nQuery: {r.query_string}, Category: {r.category}\n")
        print(f"Cheapest: {'': ^20}{r.min_priced_item.comparison_price:.2f}{'':<2}€/{r.min_priced_item.comparison_unit}{'':^7}{r.min_priced_item.name}")
        print(f"Most expensive: {'': ^14}{r.max_priced_item.comparison_price:.2f}{'':<2}€/{r.min_priced_item.comparison_unit}{'':^7}{r.max_priced_item.name}")
        print(f"Average price: {'': ^15}{r.avg_priced_item:.2f}{'':<2}€/{r.min_priced_item.comparison_unit}")

    ProductList.update_total_cost()
    print("\n")
    print(f"Min: {'': ^25}{ProductList.total_cost_cheapest:.2f}€")
    print(f"Max: {'': ^25}{ProductList.total_cost_expensive:.2f}€")
    print(f"Avg: {'': ^25}{ProductList.total_cost_avg:.2f}€")
    print("")