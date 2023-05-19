import {delay, get, post} from "./utils.js";

var storeQueries = [];
var productQueries = [];

const addStoreBtn = document.getElementById("store_add_btn");
const addQueryBtn = document.getElementById("query_add_btn");

const storeInput = document.getElementById("store-input");
const storesList = document.querySelector(".stores-list");

//addStoreBtn.addEventListener("click", addStoreQuery);
//addQueryBtn.addEventListener("click", addProductQuery);
storeInput.addEventListener("input", delay(queryStore, 1250))


function queryStore() {
    get("/store/query/", {value: storeInput.value}).then(response => {
        addStoreQuery(response["result"]);
        console.log(JSON.stringify(response));
    })
};


function addStoreQuery(store) {
    if (!storeQueries.includes(store)) {
        storeQueries.push(store);
    }
}

function removeStoreQuery(store) {
    let index = storeQueries.indexOf(store);
    if (!(index === -1)) {
        storeQueries.splice(index, 1);
    }
}