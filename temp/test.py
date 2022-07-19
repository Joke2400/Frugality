from data.urls import SKaupatURLs as s_urls
import requests

def run(store_id):
    api_url = s_urls.api_url
    query1 = """query GetDeliveryAreas($deliveryMethod: DeliveryMethod, $brand: String, $onlySKaupat: Boolean, $postalCode: String) {
        deliveryAreas(
            deliveryMethod: $deliveryMethod
            brand: $brand
            onlySKaupat: $onlySKaupat
            postalCode: $postalCode
        ) {
                areaId
                store {
                    name
                    id
                    brand
                    __typename
                }
        }
    }
    """
    query2 = """query GetStoreInfo($StoreID: ID!) {
        store(id: $StoreID) {
            name
            id
            brand
            __typename
        }
    }
    """
    operation_name = "GetStoreInfo"
    variables = {
        "StoreID": int(store_id)
    }
    
    post_request = requests.post(url=api_url, json={
        "operationName": operation_name,
        "variables": variables,
        "query": query2
        })
    return post_request.text