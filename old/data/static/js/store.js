export { storeQuery, storesList, buildStoreQueries };
import { post, del, refreshChildren, dom, domStyle, delay } from "./utils.js";

var mouseHover = false;

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

// STORE RESULT FUNCTIONS

function storeQuery() {
    let element = storeBox.querySelector("." + dom.storeContainer);
    let value = storeInput.value
    if (element !== null) {
        storeBox.removeChild(element);
    }
    // Yes this function is disgustingly nested, shh...
    if (value.length !== 0) {
        if (value !== previousQuery[0]) {
            post("/store/query/", {value: value}).then(response => response.json())
            .then(response => {
                if ("message" in response) {
                    console.log(response["message"]);
                }
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
        storeInput.classList.remove(
            domStyle.roundedTop,
            domStyle.borderBottomLight)
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
        storeBox.appendChild(resultBox);
    }
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
            {store: store}).then(response => response.json())
            .then(response => {
                if ("result" in response) {
                    storeQueries = response["result"];
                }
                console.log(`storeQueries: [${storeQueries}]`)
                hideStoreResults(true)
                refreshChildren(storesList, storeQueries,
                    buildStoreQueries);
            })
    }
}


function removeStoreQuery(store) {
    if (storeQueries.includes(store)) {
        del("/store/query/select/",
            {id: store[1]}).then(response => response.json())
            .then(response => {
                if ("result" in response) {
                    storeQueries = response["result"];
                }
                console.log(`storeQueries: [${storeQueries}]`)
                refreshChildren(storesList, storeQueries,
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
    li.classList.add(dom.storeItem);

    let p = document.createElement("p");
    p.classList.add(dom.storeItemText, domStyle.rounded, domStyle.bottomShadow)
    p.innerText = store[0];

    let btn = document.createElement("button");
    btn.classList.add(domStyle.bottomShadow)
    btn.innerText = "-";
    btn.addEventListener("click", e => {
        removeStoreQuery(store)
    })
    li.appendChild(p);
    li.appendChild(btn);
    return li
}
