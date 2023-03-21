
function sendProductQuery() {
    let fetchData = {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }
    fetch("/product_query/", fetchData).then(response => response.json())
    .then(function() {
        location.reload();
    });
}

function addStore() {
    let store = document.getElementById("store-input").value;
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            store: store
        })
    }
    fetch("/add_store/", fetchData).then(response => response.json())
    .then(function(data) {
        refreshStores(data["stores"]);
    });
}

function addProductQuery() {
    let query = document.getElementById("query-input").value;
    let count = 1;
    let category = "";
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query,
            count: count,
            category: category
        })
    }
    fetch("/add_query/", fetchData).then(response => response.json())
    .then(function(data) {
        refreshQueries(data["queries"]);
    });
}

function refreshQueries(queries) {
    const elements = document.getElementsByClassName("query-item")
    while(elements.length > 0) {
        elements[0].parentNode.removeChild(elements[0]);
    }
    let queryList = document.querySelector(".queries-list");
    for (let i = 0; i < queries.length; i++) {
        item = createQueryItem(queries[i], i);
        queryList.appendChild(item);
    }

}

function refreshStores(stores) {
    const elements = document.getElementsByClassName("store-item");
    while(elements.length > 0) {
        elements[0].parentNode.removeChild(elements[0]);
    }
    let storesList = document.querySelector(".stores-list");
    for (let i = 0; i < stores.length; i++) {
        item = createStoreItem(stores[i], i);
        storesList.appendChild(item);
    }

}

function createStoreItem(tup, inx) {
    let name = document.createElement("p");
    name.classList.add("store-msg", "rounded", "shadow");
    name.innerText = tup[0];
    let btn = document.createElement("button");
    btn.innerText = "-";
    btn.onclick = function() {
        removeStore(inx)
    };
    let li = document.createElement("li");
    li.classList.add("store-item");
    li.appendChild(name);
    li.appendChild(btn);

    return li
}


function createQueryItem(dict, inx) {
    let amount = document.createElement("p");
    amount.classList.add("count")
    amount.innerText = dict["count"] + "x";
    let name = document.createElement("p");
    name.classList.add("name");
    name.innerText = dict["query"];
    let category = document.createElement("p");
    category.classList.add("category");
    category.innerText = dict["category"];

    let textDiv = document.createElement("div")
    textDiv.classList.add("item-text")
    textDiv.appendChild(name);
    textDiv.appendChild(category);

    let btn = document.createElement("button");
    btn.classList.add("btn", "rounded-more");
    btn.innerText = "-";
    btn.onclick = function() {
        removeProductQuery(inx);
    }

    let queryItemData = document.createElement("div");
    queryItemData.classList.add("query-data");
    queryItemData.appendChild(amount);
    queryItemData.appendChild(textDiv)
    queryItemData.appendChild(btn);

    let queryItem = document.createElement("div");
    queryItem.classList.add("query-item", "rounded-more", "shadow");
    queryItem.appendChild(queryItemData);

    return queryItem;
}

function removeProductQuery(inx) {
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            index: inx
        })
    }
    fetch("/remove_query/", fetchData).then(response => response.json())
    .then(function(data) {
        refreshQueries(data["queries"]);
    });
}

function removeStore(inx) {
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            index: inx
        })
    }
    fetch("/remove_store/", fetchData).then(response => response.json())
    .then(function(data) {
        refreshStores(data["stores"]);
    });
}