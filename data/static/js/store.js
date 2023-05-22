export { storeQuery, displayStoreResults, hideStoreResults };
import { get, post, refreshList } from "./utils.js"

window.onload = e => {
    get("/stores/").then(response => {
        window.storeQueries = response["stores"];
        refreshList(storesList, storeQueries,
            buildStoreQueries);
})}

const storeBox = document.querySelector(".store-box");
const storeInput = document.getElementById("store-input");
const storesList = document.querySelector(".stores-list");

var previousQuery = ["", []]

function storeQuery() {
    let element = storeBox.querySelector(".store-result-container");
    let value = storeInput.value
    if (value.length !== 0) {
        if (value !== previousQuery[0]) {
            if (element !== null) {
                storeBox.removeChild(element);
            }
            get("/store/query/", {value: value}).then(response => {
                createStoreResultsDialog(response);
                previousQuery = [value, response]
                storeInput.style = "outline: none;"
                storeInput.classList.add("rounded-top", "border-bottom-light")
            })
        } else {
            createStoreResultsDialog(previousQuery[1])
            storeInput.style = "outline: none;"
            storeInput.classList.add("rounded-top", "border-bottom-light")
        }
    } else {
        hideStoreResults()
    }
};



function displayStoreResults() {
    let resultBox = document.querySelector(".store-result-container");
    if (resultBox !== null) {
        resultBox.style = "display: flex;"
        storeInput.style = "outline: none;"
        storeInput.classList.add("rounded-top", "border-bottom-light")
    }
}


function hideStoreResults() {
    let resultBox = document.querySelector(".store-result-container");
    if (resultBox !== null) {
        resultBox.style = "display: none;"
        storeInput.classList.remove("rounded-top", "border-bottom-light")
    }
}


function createStoreResultsDialog(response) {
    if ("stores" in response) {
        var resultBox = createStoreContainer();
        var resultList = resultBox.firstChild
        let length = response["stores"].length;
        for (let i = 0; i < length; i++) {
            resultList.appendChild(
                createStoreResultItem(response["stores"][i]));
        }
    }
    storeBox.appendChild(resultBox);
}


function createStoreContainer() {
    let resultBox = document.createElement("div");;
    resultBox.classList.add(
        "store-result-container",
        "bottom-shadow",
        "rounded-bottom");
    resultBox.appendChild(document.createElement("ul"))
    return resultBox
}


function createStoreResultItem(item) {
    let listItem = document.createElement("li");
    listItem.classList.add("store-result-item");
    let btn = document.createElement("button");
    btn.classList.add("store-result-btn");
    btn.classList.add("border-bottom-light");
    btn.innerText = item["name"]
    btn.addEventListener("click", e => {
        addStoreQuery(
            [item["name"],
            item["store_id"],
            item["slug"]]);
    })
    listItem.appendChild(btn)
    return listItem
}


function addStoreQuery(store) {
    if (!storeQueries.includes(store)) {
        post("/store/query/select/",
            {store: store})
            .then(response => {
                if ("message" in response) {
                    console.log(response["message"]);
                }
                if ("result" in response) {
                    if (response["result"] === true) {
                        storeQueries.push(store);
                    }
                }
                console.log(`storeQueries: [${storeQueries}]`)
                refreshList(storesList, storeQueries,
                    buildStoreQueries);
            })
    }
}


function removeStoreQuery(store) {
    let index = storeQueries.indexOf(store);
    if (storeQueries.includes(store)) {
        get("/store/query/select/",
            {id: store[1]})
            .then(response => {
                if ("message" in response) {
                    console.log(response["message"]);
                }
                if ("result" in response) {
                    if (response["result"] === true) {                        
                        storeQueries.splice(index, 1);
                    }
                }
                console.log(`storeQueries: [${storeQueries}]`)
                refreshList(storesList, storeQueries,
                    buildStoreQueries);
            })
    }
}


function buildStoreQueries(stores) {
    for (let i = 0; i < stores.length; i++) {
        let storeItem = createStoreItem(stores[i]);
        storesList.appendChild(storeItem);
    }
}


function createStoreItem(store) {
    let li = document.createElement("li");
    li.classList.add("store-item");

    let p = document.createElement("p");
    p.classList.add("store-item-txt", "rounded", "shadow")
    p.innerText = store[0];

    let btn = document.createElement("button");
    btn.classList.add("shadow")
    btn.innerText = "-";
    btn.addEventListener("click", e => {
        removeStoreQuery(store)
    })
    li.appendChild(p);
    li.appendChild(btn);
    return li
}
