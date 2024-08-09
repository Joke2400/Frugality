
export interface Store {
    store_id: number;
    store_name: string;
    slug: string;
    brand: string;
}

export interface Product {}


export interface StoreQuery {
    storeId: number | null;
    storeName: string | null;
}

export interface StoreResponse {
    results: Store[];
}

export interface ProductQuery {}

export interface ProductResponse {}
