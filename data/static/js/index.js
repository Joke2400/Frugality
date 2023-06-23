import { productsList, buildProductQueries } from "./product.js"
import { storesList, buildStoreQueries } from "./store.js";
import { get, refreshList} from "./utils.js";

window.onload = e => {
    get("/stores/").then(response => {
        window.storeQueries = response["stores"];
        localStorage.setItem("storeQueries", JSON.stringify(response["stores"]))
        refreshList(storesList, storeQueries,
            buildStoreQueries);
    })
    get("/products/").then(response => {
        window.productQueries = response["products"];
        localStorage.setItem("productQueries", JSON.stringify(response["products"]))
        refreshList(productsList, productQueries,
            buildProductQueries);
    })
}