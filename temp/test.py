from data.urls import SKaupatURLs as s_urls
from urllib.parse import quote
import requests
from api import app

def run():


    app.run()

    api_url = s_urls.api_url
    operation = "GetDeliveryAreas"
    variables={"brand": "",
               "onlySKaupat": "true",
               "postalCode": "",
               "deliveryMethod":
               "PICKUP"}
    
    query_url = f"{api_url}?operationName={operation}&variables=" + quote(r"{'brand':'','onlySKaupat':'true','postalCode':'','deliveryMethod':'pickup'}&extensions=")
    query_url = query_url + quote(r"&extensions={'persistedQuery':{'version':1,'sha256Hash':'b013b0172813fd0b8fe0448a982f84ae9b7c52b3f1b58cdf887dab74134b3b3f'}}")
    print(query_url)

    r = requests.get(query_url)
    print(r.status_code)
    print(r.text)