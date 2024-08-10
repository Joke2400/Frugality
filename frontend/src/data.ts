
export class Store {

    public storeId: number;
    public storeName: string;
    public slug: string;
    public brand: string;

    constructor(storeId: number, storeName: string, slug: string, brand: string) {
        this.storeId = storeId;
        this.storeName = storeName;
        this.slug = slug;
        this.brand = brand;
    }

    public asSnakeCase(): 
        {store_id: number, store_name: string, slug: string, brand: string} {
        return {
            store_id: this.storeId,
            store_name: this.storeName,
            slug: this.slug,
            brand: this.brand
        };
    }

    public getIdentifiers(): {id: number, name: string} {
        return {
            id: this.storeId,
            name: this.storeName,
        };
    }
}

export interface Product {}

export interface StoreResponse {
    results: {store_id: number, store_name: string, slug: string, brand: string}[];
}

export interface ProductResponse {}
