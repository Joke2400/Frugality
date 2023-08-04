import { dom, domStyle, refreshChildren, createCustomElement, clearNodeChildren, appendToParentInOrder, appendNewTextElement} from "./utils.js";

const main = document.getElementById("main");
let currentFilter = "FIRST";

window.onload = e => {
    window.searchResults = JSON.parse(localStorage.getItem("results"));
    refreshChildren(main, searchResults, buildResultPage);
};

function buildResultPage(results) {
    for (let i = 0; i < results.length; i++) {
        main.appendChild(createPageSection(results[i][1]))
    }
};

function createPageSection(queries) {
    let section = createCustomElement("section", dom.storeSection);
    let storeHeaderDiv = createCustomElement("div", dom.storeHeader);
    let resultsList = createCustomElement("ul", dom.verticalList, dom.resultsList);

    appendNewTextElement(storeHeaderDiv, "h3", queries[0]["store"][0]);
    appendNewTextElement(storeHeaderDiv, "h4", queries.length + " queries retrieved.");
    appendToParentInOrder(section, storeHeaderDiv, resultsList)
   
    // Append result items
    for (let i = 0; i < queries.length; i++) {
        resultsList.appendChild(createResultItem(queries[i]["query"], queries[i]["products"]))
    }
    return section
}


// Result item creation functions
function createResultItem(query, products) {
    let item = createCustomElement("li", dom.resultItem);
    item.query = query;
    item.products = products;
    
    // Temporary, add filtering code here
    let displayedProduct = products[0];

    appendItemData(item, query, products, displayedProduct);
    return item
}

function refreshDisplayItem(item, displayedProduct) {
    clearNodeChildren(item);
    appendItemData(item, item.query, item.products, displayedProduct);
}

function appendItemData(parentItem, query, products, displayedProduct) {
    let itemCount = buildItemCount(query["count"]);
    let productData = buildProductData(
        displayedProduct["name"], displayedProduct["category"], query["query"]);
    let priceData = buildPriceData(displayedProduct["price_data"]);

    let dropdownBtn = buildDropdownBtn(parentItem, products, displayedProduct);

    appendToParentInOrder(parentItem, itemCount, productData, dropdownBtn, priceData);
}


function buildItemCount(count) {
    let p = createCustomElement("p", dom.count);
    p.innerText = count + "x";
    return p
}

function buildProductData(name, category, queryString) {
    let productData = createCustomElement("div", dom.productData);
    appendNewTextElement(productData, "p", "Search: '" + queryString + "'");
    appendNewTextElement(productData, "p", name);
    appendNewTextElement(productData, "p", category);
    return productData
}

function buildPriceData(data) {
    let priceData = createCustomElement("div", dom.priceData);
    let nestedDiv = document.createElement("div");

    appendNewTextElement(nestedDiv, "p", data[0] + "€");
    appendNewTextElement(nestedDiv, "p", "/" + data[1]);

    priceData.appendChild(nestedDiv);
    appendNewTextElement(priceData, "p", data[2] + "€/" + data[3])
    return priceData
}

// Dropdown logic ---------------------------------------------------------

function buildDropdownBtn(parentItem, products, displayedProduct) {
    let dropdownBtn = createCustomElement("button", dom.dropdownBtn);
    dropdownBtn.innerText = "X"
    dropdownBtn.addEventListener("click", event => {
        toggleDropdown(parentItem, dropdownBtn, products, displayedProduct);
    })
    return dropdownBtn
}

function toggleDropdown(parentItem, dropdownBtn, products, displayedProduct) {
    if (dropdownBtn.children.length !== 0) {
        clearNodeChildren(dropdownBtn);
    } else {
        let items = buildDropdownItems(parentItem, products, displayedProduct);
        dropdownBtn.appendChild(items);
    }

}

function buildDropdownItems(parentItem, products, displayedProduct) {
    let items = createCustomElement("ul", dom.dropdown, dom.verticalList);
    for (let i = 0; i < products.length; i++) {
        if (i !== products.indexOf(displayedProduct)) {
            let li = createCustomElement("li", dom.dropdownItem);
            let btn = document.createElement("button");
            btn.innerText = products[i]["name"];
            btn.addEventListener("click", event => {
                refreshDisplayItem(parentItem, products[i]);
            })
            li.appendChild(btn);
            items.appendChild(li)
        }
    }
    return items
}

function refreshSections() {
    
}