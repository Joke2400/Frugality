import { dom, refreshChildren, createCustomElement, clearNodeChildren, appendToParentInOrder, appendH3Element, appendH4Element, appendParagraph} from "./utils.js";

const mainNode = document.getElementById("main");
const storedResults = JSON.parse(localStorage.getItem("results")); // Get stored results
let pageSections = [];

// CSS element class definitions
const defs = {
    // used in <section>
    storeHeader: "store-header",
    sectionBody: "section-body",
    productColumn: "product-column",
    priceTotalColumn: "price-total-column",
    priceDetailColumn: "price-detail-column",

    // used in productColumn
    resultItem: "result-item",
    productCount: "product-count",
    productData: "product-data",
    dropdownBtn: "dropdown-btn",

    // used in priceColumn
    priceTotal: "price-total",
    priceDetail: "price-detail",
}

// CSS class definitions for simple attributes, ex. shadow, border
const attr = {

}
window.onload = e => {
    refreshChildren(mainNode, storedResults, buildPage);
    // Clear mainNode children and load page using buildPage func
};
// ---------------------------------------------------------
// Page section creation funcs
// ---------------------------------------------------------
function buildPage(storedResults) {
    for (let i = 0; i < storedResults.length; i++) {
        let section = buildSection(storedResults[i][1])
        pageSections.push(section);
        mainNode.appendChild(section.getNode());
    }
}

function buildSection(queriesList) {
    let section = {
        results: buildResults(queriesList),
        getNode: function() {
            let node = document.createElement("section");
            let header = createCustomElement("div", defs.storeHeader);
            appendH3Element(header, queriesList[0]["store"][0]);
            appendH4Element(header, queriesList.length + " queries retrieved.");
            node.appendChild(header);

            let body = createCustomElement("div", defs.sectionBody);
            let productColumn = this.results.getProductColumnNode();
            let priceDetail = this.results.getPriceDetailColumnNode();
            let priceTotal = this.results.getPriceTotalColumnNode();
            appendToParentInOrder(body, productColumn, priceDetail, priceTotal);
            node.appendChild(body);
            
            return node
        }
        
    }
    return section
}
// ---------------------------------------------------------
// Results list creation
// ---------------------------------------------------------
function buildResults(queriesList) {
    let results = {
        items: buildResultItems(queriesList),
        getProductColumnNode: function() {
            let node = createCustomElement("ul", defs.productColumn);
            for (let i = 0; i < this.items.length; i++) {
                node.appendChild(this.items[i].getProductNode());
            }
            return node
        },
        getPriceTotalColumnNode: function() {
            let node = createCustomElement("ul", defs.priceTotalColumn);
            for (let i = 0; i < this.items.length; i++) {
                node.appendChild(this.items[i].getPriceTotalNode());
            }
            return node
        },
        getPriceDetailColumnNode: function() {
            let node = createCustomElement("ul", defs.priceDetailColumn);
            for (let i = 0; i < this.items.length; i++) {
                node.appendChild(this.items[i].getPriceDetailNode());
            }
            return node
        }
    }
    return results
}

function buildResultItems(list) {
    let items = [];
    for (let i = 0; i < list.length; i++) {
        let queryItem = list[i];
        const newItem = {
            selectedProduct: queryItem["products"][0],
            products: queryItem["products"],
            query: queryItem["query"],
            getProductNode: function() {
                let node = createCustomElement("li", defs.resultItem);
                let dropdownBtn = buildDropdownBtn(
                    node, this.products, this.selectedProduct);
                let itemCount = buildItemCount(this.query["count"]);
                let itemText = buildItemText(
                    this.query["query"],
                    this.selectedProduct["category"],
                    this.selectedProduct["name"]);
                appendToParentInOrder(node, dropdownBtn, itemCount, itemText)
                return node
            },
            getPriceTotalNode: function() {
                return buildPriceTotal(this.selectedProduct["price_data"], this.query["count"]);
            },
            getPriceDetailNode: function() {
                return buildPriceDetail(this.selectedProduct["price_data"]);
            }
        }
        items.push(newItem);
    }
    return items
}
// ---------------------------------------------------------
// Item data element creation
// ---------------------------------------------------------
function buildItemCount(count) {
    let node = createCustomElement("p", defs.productCount);
    node.innerText = count + "x";
    return node
}

function buildItemText(name, category, queryString) {
    let node = createCustomElement("div", defs.productData);
    appendParagraph(node, "Search: '" + queryString + "'");
    appendParagraph(node, name);
    appendParagraph(node, category);
    return node
}

function buildPriceDetail(data) {
    let node = createCustomElement("div", defs.priceDetail);
    appendParagraph(node, data[0] + "€/" + data[1].toLowerCase());
    appendParagraph(node, data[2] + "€/" + data[3])
    return node
}

function buildPriceTotal(data, count) {
    let node = createCustomElement("div", defs.priceTotal);
    appendParagraph(node, (data[0] * count).toFixed(2) + "€");
    return node
}
// ---------------------------------------------------------

function buildDropdownBtn(parentItem, products, displayedProduct) {
    let dropdownBtn = createCustomElement("button", defs.dropdownBtn);
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
    // Order dropdown items alphabetically
    let ordered = products.sort((a, b) => {
        const keyA = a.name.toUpperCase();
        const keyB = b.name.toUpperCase();
        return keyA.localeCompare(keyB);
    })
    for (let i = 0; i < ordered.length; i++) {
        if (i !== ordered.indexOf(displayedProduct)) {
            let item = ordered[i];
            let priceStr = item["price_data"][0] + "€/" + item["price_data"][1];
            let nameStr = "  |  " + item["name"];


            let li = createCustomElement("li", dom.dropdownItem);
            let btn = document.createElement("button");
            btn.innerText = priceStr + nameStr;
            btn.addEventListener("click", event => {
                refreshProductLists(parentItem.query["query"], ordered[i].ean);
            })
            li.appendChild(btn);
            items.appendChild(li)
        }
    }
    return items
}

// Functions for updating displayed data
function refreshResultItem(item, newDisplayedProduct) {
    item.displayedProduct = newDisplayedProduct;
    clearNodeChildren(item);
    appendItemData(item, item.query, item.products, newDisplayedProduct);
}

function refreshProductLists(queryToRefresh, newDisplayProductEan) {
    let lists = document.getElementsByClassName(dom.resultsList);
    for (let resultsList of lists) {
        for (let resultItem of resultsList.children) {
            let query = resultItem.query["query"]
            if (queryToRefresh === query) {
                let hasChanged = false;
                for (let i = 0; i < resultItem.products.length; i++) {
                    let product = resultItem.products[i];
                    if (product.ean === newDisplayProductEan) {
                        refreshResultItem(resultItem, product);
                        hasChanged = true;
                        break
                    }
                }
                if (hasChanged === false) {
                    resultItem.style = "background: red" //temp
                }
            }
        }
        //refreshlistOverview()
    }
}

