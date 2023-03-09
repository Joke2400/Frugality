
function sendQuery() {
    let queries = [];
    let amounts = [];
    let categories = [];
    document.querySelectorAll(".item_name").forEach(r => queries.push(r.innerText));
    document.querySelectorAll(".item_amount").forEach(r => amounts.push(r.innerText));
    document.querySelectorAll(".item_category").forEach(r => categories.push(r.innerText));
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            queries: queries,
            amounts: amounts,
            categories: categories
        })
    }
    fetch("/query/", fetchData).then(response => response.json())
    .then(function() {
        location.reload();
    });
}

function addQuery() {
    let query = document.getElementById("query_input").value;
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
    const elements = document.getElementsByClassName("query_item container")
    while(elements.length > 0) {
        elements[0].parentNode.removeChild(elements[0]);
    }
    let queryList = document.querySelector(".items_container");
    for (let i = 0; i < queries.length; i++) {
        item = createQueryItem(queries[i])
        queryList.insertBefore(item, queryList.children[queryList.children.length - 1])
    }

}

function createQueryItem(dict) {
    let amount = document.createElement("p");
    amount.classList.add("item_amount")
    amount.innerText = dict["count"] + "x";
    let name = document.createElement("p");
    name.classList.add("item_name");
    name.innerText = dict["query"];

    let dataDiv = document.createElement("div")
    dataDiv.appendChild(amount);
    dataDiv.appendChild(name);

    let category = document.createElement("p");
    category.classList.add("item_category");
    category.innerText = dict["category"];

    let queryItemData = document.createElement("div");
    queryItemData.classList.add("query_item_data");
    queryItemData.appendChild(dataDiv);
    queryItemData.appendChild(category);

    let btn = document.createElement("button");
    btn.classList.add("input_button");
    btn.innerText = "-";
    let queryItem = document.createElement("div");
    queryItem.classList.add("query_item", "container");
    queryItem.appendChild(queryItemData);
    queryItem.appendChild(btn);

    return queryItem;
}
