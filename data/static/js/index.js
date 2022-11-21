var productAddBtn = document.querySelector(".product-add-btn");
productAddBtn.addEventListener('click', function() {
    addQuery();
})


function addQuery() {
    var queryValue = document.querySelector(".query-input").value;
    let queryList = document.querySelector(".query-items-list");
    if (queryValue === "") {
        return 0;
    };
    let existingItem = null;
    let items = queryList.querySelectorAll(".query-item");
    for (let i = 0; i< items.length; i++) {
        let item = items[i].firstChild.children[1];
        if (item.innerText === queryValue) {
            existingItem = item.parentElement;
        };
    };
    if (existingItem !== null) {
        increaseAmount(existingItem);
    } else {
        queryItem = createQueryItem(queryValue);
        queryList.appendChild(queryItem);
    };
};

function increaseAmount(item) {
    let amtChild = item.firstChild;
    let value = parseInt(amtChild.innerText.replace(/\D/g,''), 10) + 1;
    value += "x";
    amtChild.innerText = value;
};

function decreaseAmount(item) {
    let amtChild = item.firstChild;
    let value = parseInt(amtChild.innerText.replace(/\D/g,''), 10) - 1;
    if (value === 0) {
        removeQueryItem(item.parentElement);
    } else {
        value += "x";
        amtChild.innerText = value;
    }
}

function createQueryItem(queryValue) {
    let amount = document.createElement("p");
    let name = document.createElement("p");
    let btn = document.createElement("button");
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
        decreaseAmount(itemData)
    })

    itemData.classList.add("item-data");

    itemData.appendChild(amount);
    itemData.appendChild(name);
    itemData.appendChild(btn);

    queryItem.classList.add("query-item");
    queryItem.appendChild(itemData);
    
    return queryItem;
};

function removeQueryItem(queryItem) {
    queryItem.remove();
}

function selectStore() {

};
