queries = {}

queries["GetDeliveryAreas"] = """query GetDeliveryAreas($deliveryMethod: DeliveryMethod, $brand: String, $onlySKaupat: Boolean, $postalCode: String) {
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

queries["GetStoreInfo"] = """query GetStoreInfo($StoreID: ID!) {
        store(id: $StoreID) {
            name
            id
            brand
            __typename
        }
    }
    """