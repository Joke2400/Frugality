from data.urls import SKaupatURLs as s_urls
from urllib.parse import quote
import requests

def run():
    query1 = """query {
        deliveryArea(id: "ad3fa780-6afb-49da-8513-0c48753b0a7f") {
            name
        }
    }"""
    query2 = """query {
        __schema {
            types {
                name
            }
        }
    }"""

    api_url = s_urls.api_url
    r = requests.post(url=api_url, json={"query": query1})
    print(r.status_code)
    print(r.text)