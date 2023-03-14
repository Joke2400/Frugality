
function sendQuery() {
    let fetchData = {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }
    fetch("/query/", fetchData).then(response => response.json())
    .then(function() {
        location.reload();
    });
}

function addQuery() {
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
    const elements = document.getElementsByClassName("query-item container")
    while(elements.length > 0) {
        elements[0].parentNode.removeChild(elements[0]);
    }
    let queryList = document.querySelector(".list");
    for (let i = 0; i < queries.length; i++) {
        item = createQueryItem(queries[i], i);
        queryList.appendChild(item);
    }

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
    btn.classList.add("btn");
    btn.innerText = "-";
    btn.onclick = function() {
        removeQuery(inx);
    }

    let queryItemData = document.createElement("div");
    queryItemData.classList.add("query-data");
    queryItemData.appendChild(amount);
    queryItemData.appendChild(textDiv)
    queryItemData.appendChild(btn);

    let queryItem = document.createElement("div");
    queryItem.classList.add("query-item", "container");
    queryItem.appendChild(queryItemData);

    return queryItem;
}

function removeQuery(inx) {
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