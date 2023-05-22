import { storeQuery, displayStoreResults, hideStoreResults } from "./store.js";
import { delay } from "./utils.js";

var productQueries = [];

const addStoreBtn = document.getElementById("store_add_btn");
const addQueryBtn = document.getElementById("query_add_btn");

const storeInput = document.getElementById("store-input");
const storesList = document.querySelector(".stores-list");

//addStoreBtn.addEventListener("click", testFunc2);
//addQueryBtn.addEventListener("click", addProductQuery);
storeInput.addEventListener("input", event => {
    event.target.style = "color: '';";
})

storeInput.addEventListener("input", delay(storeQuery, 600));

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