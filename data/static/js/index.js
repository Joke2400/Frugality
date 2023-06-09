import { addProductQuery, productsList, buildProductQueries } from "./product.js"
import { storeQuery, displayStoreResults, hideStoreResults, storesList, buildStoreQueries } from "./store.js";
import { delay, dom, get, refreshList} from "./utils.js";

const addQueryBtn = document.getElementById(dom.queryAddBtn);
const storeInput = document.getElementById(dom.storeInput);
const sendQueryBtn = document.getElementById(dom.sendQueryBtn)

window.onload = e => {
    get("/stores/").then(response => {
        window.storeQueries = response["stores"];
        refreshList(storesList, storeQueries,
            buildStoreQueries)
    })
    get("/products/").then(response => {
        window.productQueries = response["products"];
        refreshList(productsList, productQueries,
            buildProductQueries);
    })
}

sendQueryBtn.addEventListener("click", event => {
    get("/product/query/").then(response => {
        if ("url" in response) {
            location.href = response["url"];
        }
    })
})

addQueryBtn.addEventListener("click", event => {
    let name = document.getElementById(dom.queryInput).value;
    if (name !== "") {
        let product = {
            query: name,
            count: 1,
            category: "",
        }
        addProductQuery(product);
    }
});

/* Store input element event listeners */
storeInput.addEventListener("input", delay(storeQuery, 600));
storeInput.addEventListener("input", event => {
    event.target.style = "color: '';";
})

storeInput.addEventListener("focusin", event => {
    if (storeInput.value.length === 0) {
        event.target.style = "color: transparent;";
    } else {
        displayStoreResults()
    }
});
storeInput.addEventListener("focusout", event => {
    event.target.style = "color: '';";
    hideStoreResults()
});