from data.urls import SKaupatURLs as s_urls
from urllib.parse import quote
import requests

def run():
    api_url = s_urls.api_url
    query = """query GetDeliveryAreas($deliveryMethod: DeliveryMethod, $brand: String, $onlySKaupat: Boolean, $postalCode: String) {
        deliveryAreas(
            deliveryMethod: $deliveryMethod
            brand: $brand
            onlySKaupat: $onlySKaupat
            postalCode: $postalCode
        ) {
                name
                areaId
                storeId
                price
                description
                deliveryMethod
                alcoholSellingAllowed
                isFastTrack
                store {
                    name
                    id
                    brand
                    city
                    street
                    postalCode
                    availablePaymentMethods
                    __typename
                }
                districts {
                    city
                    postalCode
                    __typename
                }
                address {
                    city
                    postalCode
                    street
                    __typename
                }
                __typename
        }
    }
    """
    operation_name = "GetDeliveryAreas"
    variables = {
        "brand": "",
        "deliveryMethod": "PICKUP",
        "onlySkaupat": True,
        "postalCode": ""
    }
    
    #query2 = "Prisma"
    #variables = {"query": query2, "brand": "", "cursor": ""}
    #operation_url = api_url + "?operationName=RemoteStoreSearch"
    #get_request = requests.get(url=operation_url, params={"variables": variables})
    #print(get_request.status_code)
    #print(get_request.text)

    post_request = requests.post(url=api_url, json={
        "operationName": operation_name,
        "variables": variables,
        "query": query
        })
    print(post_request.status_code)
    print(post_request.text)