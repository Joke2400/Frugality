var productAddBtn = document.querySelector(".product-add-btn");
productAddBtn.addEventListener('click', function() {
    addQuery();
})

var storeAddBtn = document.querySelector(".store-add-btn");
storeAddBtn.addEventListener('click', function() {
    setStore();
})

var sendQueryBtn = document.querySelector(".send-query-btn");
sendQueryBtn.addEventListener('click', function() {
    sendQuery();
})


var categories = [
    "",
    "hedelmat-ja-vihannekset-1",
    "leivat-keksit-ja-leivonnaiset-1",
    "liha-ja-kasviproteiinit-1",
    "kala-ja-merenelavat-1",
    "maito-munat-ja-rasvat-0",
    "juustot-0"
];

var categoryStrings = [
    "Select category",
    "Hedelmät ja vihannekset",
    "Leivät, keksit ja leivonnaiset",
    "Liha- ja kasviproteiinit",
    "Kala ja merenelävät",
    "Maito, munat ja rasvat",
    "Juustot"
];

addEventListener('DOMContentLoaded', _ => {
    cat_selects = document.querySelectorAll(".categories").forEach(r => {
        for (let i = 0; i< categories.length; i++) {
            let s = document.createElement("option");
            s.setAttribute("value", categories[i]);
            s.innerText = categoryStrings[i];
            r.append(s);
        }
    })
});


function addQuery() {
    var queryValue = document.querySelector(".query-input").value;
    var category = document.querySelector(".categories").value;
    var queryList = document.querySelector(".query-items-list");
    if (queryValue === "") {
        return 0;
    };
    let existingItem = null;
    let items = queryList.querySelectorAll(".query-item");
    for (let i = 0; i< items.length; i++) {
        let item = items[i].firstChild.children[1];
        let itemCategory = items[i].firstChild.children[2].dataset.category;
        if (item.innerText === queryValue && itemCategory === category) {
            existingItem = item.parentElement;
        };
    };
    if (existingItem !== null) {
        increaseAmount(existingItem);
    } else {
        queryItem = createQueryItem(queryValue, category);
        queryList.appendChild(queryItem);
    };
};

function increaseAmount(item) {
    let value = parseInt(item.firstChild.innerText.replace(/\D/g,''), 10) + 1;
    value += "x";
    item.firstChild.innerText = value;
};

function decreaseAmount(item) {
    let value = parseInt(item.firstChild.firstChild.innerText.replace(/\D/g,''), 10) - 1;
    if (value === 0) {
        removeQueryItem(item);
    } else {
        value += "x";
        item.firstChild.firstChild.innerText = value;
    }
}

function createQueryItem(queryValue, category) {
    let amount = document.createElement("p");
    let name = document.createElement("p");
    let btn = document.createElement("button");
    let cat = document.createElement("div")
    var itemData = document.createElement("div");
    let queryItem = document.createElement("div");
    amount.classList.add("amt");
    amount.innerText = "1x";

    name.classList.add("name");
    name.innerText = queryValue;
    btn.classList.add("remove-query-btn");
    btn.type = "button";
    btn.innerText = "-";
    btn.addEventListener('click', function() {
        decreaseAmount(queryItem)
    })
    cat.classList.add("category")
    cat.dataset.category = category
    for (let i = 0; i< categories.length; i++) {
        if (categories[i] === category) {
            if (i !== 0) {
                cat.innerText = categoryStrings[i]
            };
        };
    };

    itemData.classList.add("item-data");

    itemData.appendChild(amount);
    itemData.appendChild(name);
    itemData.appendChild(cat)

    queryItem.classList.add("query-item");
    queryItem.appendChild(itemData);
    queryItem.appendChild(btn);
    
    return queryItem;
};

function removeQueryItem(queryItem) {
    queryItem.remove();
}

function setStore() {
    let store = document.querySelector(".store-input").value;
    let current = document.getElementById("current-store");
    current.innerText = "Current: " + store;

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
    fetch("/set_store/", fetchData).then(response => response.json())
    .then(function(data) {
        data = JSON.stringify(data["data"])
        console.log("Set store to: " + data);
    });
}

function sendQuery() {
    let queries = [];
    let amounts = [];
    let categories = [];

    document.querySelectorAll(".name").forEach(r => 
        queries.push(r.innerText));

    document.querySelectorAll(".amt").forEach(r => 
        amounts.push(r.innerText));

    document.querySelectorAll(".category").forEach(r => 
        categories.push(r.dataset.category));

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
    .then(function(data) {
        data = JSON.stringify(data["data"])
        console.log(data);
    });
}