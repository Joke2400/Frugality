from data.urls import SKaupatURLs as s_urls
import requests

api_url = s_urls.api_url

def send_post(query, operation_name, variables):
    request = requests.post(url=api_url, json={
        "operationName": operation_name,
        "variables": variables,
        "query": query
    })
    return request

def send_get(operation_name, variables):
    payload = {"operationName": operation_name, "variables": variables}
    request = requests.get(url=api_url, params=payload)
    return request