import {delay, get, post} from "./utils.js";

var storeQueries = [];
var productQueries = [];

const addStoreBtn = document.getElementById("store_add_btn");
const addQueryBtn = document.getElementById("query_add_btn");

const storeInput = document.getElementById("store-input");
const storesList = document.querySelector(".stores-list");

//addStoreBtn.addEventListener("click", testFunc2);
//addQueryBtn.addEventListener("click", addProductQuery);
storeInput.addEventListener("input", delay(queryStore, 1250))


function queryStore() {
    let value = storeInput.value
    if (value.length !== 0) {
        get("/store/query/", {value: value}).then(response => {
            console.log(JSON.stringify(response));
        })
    }
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

function testFunc() {
    post("/store/query/select/",
        {store: ["Prisma Olari", "542862479", "prisma-olari"]})
        .then(response => {
            console.log(response["stores"]);
        })
}

function testFunc2() {
    get("/store/query/select/",
        {id: 542862479})
        .then(response => {
            console.log(response["stores"]);
        })
}