import re

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
    q, u = basic_regex("(\d+)(l|k?gm?)", s)
    return {
        "quantity": q if q != "" else None, 
        "unit":     u if u != "" else None}

def get_specifier(s):
    l = basic_regex("laktoositon", s)