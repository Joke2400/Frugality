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

queries["GetProductsByEans"] = """query GetProductsByEans($StoreID: ID!, $query: [String!]) {
        store(id: $StoreID) {
            name
            id
            brand
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
            id
            brand
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
                    brandName
                    slug
                    hierarchyPath {
                        id
                        name
                        slug
                    }
                }
            }
        }
    }
    """
