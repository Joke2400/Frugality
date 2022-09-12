
def validate_post(request):
    if request.method == "POST":
        if request.json is None:
            return False
    return True
        
