export { storeQuery, displayStoreResults, hideStoreResults };
import { get, post, refreshList } from "./utils.js"

var dom = {
    storeBox: "store-box",
    storeInput: "store-input",
    storesList: "stores-list",
    storeContainer: "store-result-container",
    storeResult: "store-result-item",
    storeResultBtn: "store-result-btn",

}

var domStyle = {
    roundedTop: "rounded-top",
    roundedBottom: "rounded-bottom",
    borderBottomLight: "border-bottom-light",
    bottomShadow: "bottom-shadow"
}

var mouseHover = false;

window.onload = e => {
    get("/stores/").then(response => {
        window.storeQueries = response["stores"];
        refreshList(storesList, storeQueries,
            buildStoreQueries);
})}

const storeBox = document.querySelector("." + dom.storeBox);
const storeInput = document.getElementById(dom.storeInput);
const storesList = document.querySelector("." + dom.storesList);

var previousQuery = ["", []]

storeBox.addEventListener("mouseleave", e => {
    mouseHover = false;
})

storeBox.addEventListener("mouseover", e => {
    mouseHover = true;
})

// STORE RESULT FUNCTIONS

function storeQuery() {
    let element = storeBox.querySelector("." + dom.storeContainer);
    let value = storeInput.value
    if (value.length !== 0) {
        if (value !== previousQuery[0]) {
            if (element !== null) {
                storeBox.removeChild(element);
            }
            get("/store/query/", {value: value}).then(response => {
                createStoreResultsDialog(response);
                previousQuery = [value, response]
                storeInput.classList.add(
                    domStyle.roundedTop,
                    domStyle.borderBottomLight)
                storeInput.style = "outline: none;"
                
            })
        } else {
            createStoreResultsDialog(previousQuery[1])
            storeInput.classList.add(
                domStyle.roundedTop,
                domStyle.borderBottomLight)
            storeInput.style = "outline: none;"
        }
    } else {
        hideStoreResults()
    }
};


function displayStoreResults() {
    let resultBox = document.querySelector("." + dom.storeContainer);
    if (resultBox !== null) {
        storeInput.classList.add(
            domStyle.roundedTop,
            domStyle.borderBottomLight)
        storeInput.style = "outline: none;"
        resultBox.style = "display: flex;"
    }
}


function hideStoreResults(ignoreMouseOver = false) {
    let resultBox = document.querySelector("." + dom.storeContainer);
    if (resultBox !== null) {
        if (ignoreMouseOver) {
            storeInput.classList.remove(
                domStyle.roundedTop,
                domStyle.borderBottomLight)
            resultBox.style = "display: none;"
        } else if (!mouseHover) {
            storeInput.classList.remove(
                domStyle.roundedTop,
                domStyle.borderBottomLight)
            resultBox.style = "display: none;"
        }
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
        dom.storeContainer,
        domStyle.bottomShadow,
        domStyle.roundedBottom);
    resultBox.appendChild(document.createElement("ul"))
    return resultBox
}


function createStoreResultItem(item) {
    let listItem = document.createElement("li");
    listItem.classList.add(dom.storeResult);
    let btn = document.createElement("button");
    btn.classList.add(dom.storeResultBtn);
    btn.classList.add(domStyle.borderBottomLight);
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

// STORE ITEM FUNCTIONS

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
                hideStoreResults(true)
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
