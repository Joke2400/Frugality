queries = {}

queries["StoreSearch"] = """query StoreSearch($brand: StoreBrand, $cursor: String, $query: String) {
        searchStores(brand: $brand, cursor: $cursor, query: $query) {
            totalCount
            cursor
            stores {
                ...storeInfo
                }
            }
        }

        fragment storeInfo on StoreInfo {
            id
            slug
            name
            brand
            location {
                address {
                ...StoreAddress
                }
            }
        }

        fragment StoreAddress on StoreAddress {
            street {
                default
            }
            postcode
            postcodeName {
                default
            }
        }
"""

queries["GetStoreInfo"] = """query GetStoreInfo($StoreID: ID!) {
        store(id: $StoreID) {
            name
            id
            brand6413605229549
        }
    }
    """

queries["GetProductsByEans"] = """query GetProductsByEans($StoreID: ID!, $query: [String!]) {
        store(id: $StoreID) {
            name
            products(
                includeAgeLimitedByAlcohol: true
                searchProvider: elasticsearch
                eans: $query
            ) {
                items {
                    name
                    ean
                    price
                    basicQuantityUnit
                    comparisonPrice
                    comparisonUnit
                }
            }
        }
    }
    """

queries["GetProductByName"] = """query GetProductByName($StoreID: ID!, $query: String, $limit: Int, $slugs: String) {
        store(id: $StoreID) {
            name
            products(
                limit: $limit
                includeAgeLimitedByAlcohol: true
                searchProvider: elasticsearch
                queryString: $query
                slug: $slugs
            ) {
                items {
                    name
                    ean
                    price
                    basicQuantityUnit
                    comparisonPrice
                    comparisonUnit
                }
            }
        }
    }
    """