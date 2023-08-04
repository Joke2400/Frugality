import { dom, domStyle, refreshChildren, createCustomElement, appendToParentInOrder, appendNewTextElement} from "./utils.js";

const main = document.getElementById("main");
let currentFilter = "FIRST";

window.onload = e => {
    window.searchResults = JSON.parse(localStorage.getItem("results"));
    refreshChildren(main, searchResults, buildResults);
};

function buildResults(results) {
    for (let i = 0; i < results.length; i++) {
        main.appendChild(createResultsSection(results[i][1]))
    }
};

function createResultsSection(queries) {
    let section = createCustomElement("section", dom.storeSection);
    let storeHeaderDiv = createCustomElement("div", dom.storeHeader);
    let resultsList = createCustomElement("ul", dom.verticalList, dom.resultsList);

    appendNewTextElement(storeHeaderDiv, "h3", queries[0]["store"][0]);
    appendNewTextElement(storeHeaderDiv, "h4", queries.length + " queries retrieved.");
    appendToParentInOrder(section, storeHeaderDiv, resultsList)
   
    for (let i = 0; i < queries.length; i++) {
        resultsList.appendChild(createResultItem(queries[i]))
    }
    return section
}


// Result item creation functions
function createResultItem(queryItem) {
    let query = queryItem["query"];
    let products = queryItem["products"];
    let item = createCustomElement("li", dom.resultItem);
    
    // Temporary
    let displayedProduct = products[0];

    appendItemCount(item, query["count"])
    appendItemData(item, displayedProduct, products, query["query"])
    
    return item
}

function appendItemCount(parent, count) {
    let p = createCustomElement("p", dom.count);
    p.innerText = count + "x";
    parent.appendChild(p);
}

function appendItemData(parent, displayedProduct, products, queryString) {
    let productData = buildProductData(displayedProduct, queryString);
    let dropdownToggle = buildDropdownBtn(parent, displayedProduct, products);
    let priceData = buildPriceData(displayedProduct["price_data"]);

    appendToParentInOrder(parent, productData, dropdownToggle, priceData);
}


function buildProductData(product, queryString) {
    let productData = createCustomElement("div", dom.productData);
    appendNewTextElement(productData, "p", "Search: '" + queryString + "'");
    appendNewTextElement(productData, "p", product["name"]);
    appendNewTextElement(productData, "p", product["category"]);
    return productData
}

function buildPriceData(data, query) {
    let priceData = createCustomElement("div", dom.priceData);
    let nestedDiv = document.createElement("div");

    appendNewTextElement(nestedDiv, "p", data[0] + "€");
    appendNewTextElement(nestedDiv, "p", "/" + data[1]);

    priceData.appendChild(nestedDiv);
    appendNewTextElement(priceData, "p", data[2] + "€/" + data[3])
    return priceData
}

function buildDropdownBtn(parentItem, displayedProduct, products) {
    let dropdown = createCustomElement("button", dom.dropdownBtn);
    let items = buildDropdownItems(parentItem, displayedProduct, products);
    dropdown.addEventListener("click", event => {
        toggleDropdown(dropdown, items);
    })
    dropdown.innerText = "Drop"
    return dropdown
}

function buildDropdownItems(parentItem, displayedProduct, products) {
    let items = createCustomElement("ul", dom.dropdown, dom.verticalList);
    for (let i = 0; i < products.length; i++) {
        if (i !== products.indexOf(displayedProduct)) {
            let li = document.createElement("li");
            let btn = document.createElement("button");
            btn.innerText = products[i]["name"];
            btn.addEventListener("click", event => {
                selectDropdownItem(parentItem, dropdown, products[i]);
            })
            li.appendChild(btn);
            items.appendChild(li)
        }
    }
    return items
}

function toggleDropdown(dropdown, products) {
    console.log(products);
    dropdown.appendChild(products);
}

function selectDropdownItem(product) {

}