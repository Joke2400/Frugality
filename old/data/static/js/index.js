import { productsList, buildProductQueries } from "./product.js";
import { storesList, buildStoreQueries } from "./store.js";
import { get, refreshChildren} from "./utils.js";

window.onload = e => {
    get("/stores/").then(response => response.json()).then(response => {
        window.storeQueries = response["stores"];
        localStorage.setItem("storeQueries", JSON.stringify(response["stores"]))
        refreshChildren(storesList, storeQueries,
            buildStoreQueries);
    })
    get("/products/").then(response => response.json()).then(response => {
        window.productQueries = response["products"];
        localStorage.setItem("productQueries", JSON.stringify(response["products"]))
        refreshChildren(productsList, productQueries,
            buildProductQueries);
    })
}