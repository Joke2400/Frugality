import { delay, refreshChildren, createCustomElement, clearNodeChildren, appendToParentInOrder, appendH3Element, appendH4Element, appendParagraph} from "./utils.js";

const mainNode = document.getElementById("main");
const storedResults = JSON.parse(localStorage.getItem("results")); // Get stored results
let pageSections = [];

// CSS element class definitions
const defs = {
    // used in <section>
    storeHeader: "store-header",
    sectionBody: "section-body",
    dropdownColumn: "dropdown-column",
    countColumn: "count-column",
    productColumn: "product-column",
    priceTotalColumn: "price-total-column",
    priceDetailColumn: "price-detail-column",

    resultItem: "result-item",
    productCountItem: "product-count-item",
    productCount: "product-count",
    countArrow: "count-arrow",
    countUpArrow: "count-up-arrow",
    countDownArrow: "count-down-arrow",
    dropdownColumnItem: "dropdown-column-item",
    dropdownBtn: "dropdown-btn",
    dropdownList: "dropdown-list",
    dropdownBar: "dropdown-bar",
    dropdownItem: "dropdown-item",
    dropdownArrow: "dropdown-arrow",
    dropdownDownArrow: "dropdown-down-arrow",
    dropdownUpArrow: "dropdown-up-arrow",
    verticalList: "vertical-list",

    priceTotal: "price-total",
    priceDetail: "price-detail",

    pageOverview: "page-overview",
    storeOverview: "store-overview",
}

// CSS class definitions for simple/basic attributes, ex. shadow, border
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
        let columns = section.getListColumns();
        mainNode.appendChild(section.getNode(columns));
        refreshStoreOverview(section);
    }
    refreshPageOverview()
}
// ---------------------------------------------------------
// Functions for updating displayed data
// ---------------------------------------------------------
function refreshPage(originalItem, newItemData) {
    const query = originalItem.query
    for (let pageSection of pageSections) {
        if (pageSection != originalItem.parentSection) {
            for (let i = 0; i < pageSection.items.length; i++) {
                let currentItem = pageSection.items[i];
                if (query["query"] !== currentItem.query["query"]) {continue};
                let itemHasChanged = false;
                for (let product of currentItem.products) {
                    if (product["ean"] === newItemData["ean"]) {
                        currentItem.displayed = product;
                        currentItem.query["count"] = originalItem.query["count"];
                        pageSection.refreshItem(currentItem);
                        itemHasChanged = true;
                        break
                    }
                }
                if (itemHasChanged === false) {
                    originalItem.applyStyle("background-color: var(--clr-highlight-yellow)");
                    currentItem.applyStyle("background-color: var(--clr-highlight-red)");
                }
                break
            }
        } else {
            originalItem.displayed = newItemData;
            pageSection.refreshItem(originalItem);
        }
        refreshStoreOverview(pageSection);
    }
    refreshPageOverview();
}
function refreshPageOverview() {
    
}

function refreshStoreOverview(section) {
    let parentNode = section.node;
    let node = createCustomElement("div", defs.storeOverview);
    let div = createCustomElement("div", "bottom-shadow");
    node.appendChild(div)

    let totalNum = section.getTotal()
    let total = createCustomElement("p", "store-total")
    total.innerText = "Total: " + totalNum.toFixed(2) + "€";
    div.appendChild(total)

    let avg = createCustomElement("p", "store-avg")
    avg.innerText = "Avg: " + (totalNum/section.items.length).toFixed(2) + "€";
    div.appendChild(avg)
    if (parentNode.children.length < 3) {
        parentNode.appendChild(node)
    } else {
        parentNode.replaceChild(node, parentNode.children[2])
    }

}

function buildSection(queries) {
    let section = {
        items: [],
        queries: queries,
        columns: [],
        node: null,
        buildResultItems: function(list) {
            let items = [];
            for (let i = 0; i < list.length; i++) {
                let newItem = buildResultItem(list[i], this)
                items.push(newItem);
            }
            return items
        },
        getTotal: function() {
            let totalNum = 0;
            for (let i = 0; i < this.items.length; i++) {
                let unitPrice = this.items[i].displayed["price_data"][0];
                console.log(unitPrice);
                totalNum += unitPrice;
            }
            console.log(totalNum)
            return totalNum
        },

        refreshAll: function() {
            // Not implemented
        },
        refreshItem: function(item) {
            let [oldNodes, newNodes] = item.getNodes();
            for (let i = 0; i < newNodes.length; i++) {
                const currentCol = this.columns[i];
                for (let y = 0; y < currentCol.children.length; y++) {
                    const oldNode = currentCol.children[y];
                    const newNode = newNodes[i];
                    if (oldNode == oldNodes[i]) {
                        currentCol.replaceChild(newNode, oldNode);
                    }
                }
            }
            item.nodes = newNodes;
        },
        getHeader: function() {
            let header = createCustomElement("div", defs.storeHeader);
            appendH3Element(header, queries[0]["store"][0]);
            appendH4Element(header, queries.length + " queries retrieved.");
            return header
        },
        getListColumns: function() {
            if (this.items.length === 0) {this.items = this.buildResultItems(this.queries)};
            let dropdownCol = createCustomElement("ul", defs.dropdownColumn);
            let countCol = createCustomElement("ul", defs.countColumn);
            let textCol = createCustomElement("ul", defs.productColumn);
            let detailCol = createCustomElement("ul", defs.priceDetailColumn);
            let totalCol = createCustomElement("ul", defs.priceTotalColumn);

            for (let i = 0; i < this.items.length; i++) {
                dropdownCol.appendChild(this.items[i].getDropdownNode())
                countCol.appendChild(this.items[i].getCountNode())
                textCol.appendChild(this.items[i].getTextNode());
                detailCol.appendChild(this.items[i].getPriceDetailNode());
                totalCol.appendChild(this.items[i].getPriceTotalNode());
            };
            return [dropdownCol, countCol, textCol, detailCol, totalCol]
        },
        getNode: function(columns) {
            let node = document.createElement("section");
            node.appendChild(this.getHeader())

            let body = createCustomElement("div", defs.sectionBody);
            appendToParentInOrder(body, ...columns);
            this.columns = columns;
            node.appendChild(body);
            this.node = node
            return node
        },
    }
    return section
}

function buildResultItem(queryItem, section) {
    const item = {
        displayed: queryItem["products"][0],
        products: queryItem["products"],
        query: queryItem["query"],
        parentSection: section,
        nodes: [],
        getDropdownNode: function() {
            let node = buildDropdownBtn(this, this.products, this.displayed);
            this.nodes.push(node);
            return node
        },
        getCountNode: function() {
            let node = buildItemCount(this);
            this.nodes.push(node);
            return node
        },
        getTextNode: function() {
            let node = buildItemText(
                this.displayed["name"],
                this.displayed["category"],
                this.query["query"]);
            this.nodes.push(node);
            return node
        },
        getPriceTotalNode: function() {
            let node = buildPriceTotal(this.displayed["price_data"], this.query["count"]);
            this.nodes.push(node);
            return node
        },
        getPriceDetailNode: function() {
            let node = buildPriceDetail(this.displayed["price_data"]);
            this.nodes.push(node);
            return node
        },
        getNodes: function() {
            let oldNodes = this.nodes;
            this.nodes = [];

            let newNodes = [];
            newNodes.push(this.getDropdownNode());
            newNodes.push(this.getCountNode());
            newNodes.push(this.getTextNode());
            newNodes.push(this.getPriceDetailNode());
            newNodes.push(this.getPriceTotalNode());
            return [oldNodes, newNodes]
        },
        applyStyle: function(string) {
            this.nodes[2].style = string
        }
    }
    return item
}
// ---------------------------------------------------------
// Item data element creation
// ---------------------------------------------------------
function buildItemCount(item) {
    let node = createCustomElement("li", defs.productCountItem);
    let btnUp = document.createElement("button");
    btnUp.appendChild(createCustomElement("div", defs.countArrow, defs.countUpArrow))
    btnUp.addEventListener("click", e => {
        item.query["count"] += 1;
        refreshPage(item, item.displayed);
    })

    let btnDown = document.createElement("button");
    btnDown.addEventListener("click", e => {
        if (item.query["count"] !== 1) {
            item.query["count"] -= 1;
            refreshPage(item, item.displayed);
        }
    })
    btnDown.appendChild(createCustomElement("div", defs.countArrow, defs.countDownArrow))
    
    let p = createCustomElement("p", defs.productCount); 
    p.innerText = item.query["count"] + "x";
    node.appendChild(btnUp);
    node.appendChild(p);
    node.appendChild(btnDown);
    return node
}

function buildItemText(name, category, queryString) {
    let node = createCustomElement("li", defs.resultItem);
    appendParagraph(node, "Search: '" + queryString + "'");
    appendParagraph(node, name);
    appendParagraph(node, category);
    return node
}

function buildPriceDetail(data) {
    let node = createCustomElement("li", defs.priceDetail);
    appendParagraph(node, data[0] + "€/" + data[1].toLowerCase());
    appendParagraph(node, data[2] + "€/" + data[3])
    return node
}

function buildPriceTotal(data, count) {
    let node = createCustomElement("li", defs.priceTotal);
    appendParagraph(node, (data[0] * count).toFixed(2) + "€");
    return node
}
// ---------------------------------------------------------
// Dropdown logic
// ---------------------------------------------------------
function buildDropdownBtn(parentItem, products, displayedProduct) {
    let node = createCustomElement("li", defs.dropdownColumnItem);
    let btn = createCustomElement("button", defs.dropdownBtn);
    let arrow = createCustomElement("div", defs.dropdownArrow, defs.dropdownDownArrow);
    btn.appendChild(arrow);
   
    btn.isMouseOver = false
    btn.addEventListener("click", event => {
        toggleDropdown(parentItem, btn, products, displayedProduct);
    })
    btn.addEventListener("mouseenter", e => {
        btn.isMouseOver = true
    })
    btn.addEventListener("mouseleave", e => {
        btn.isMouseOver = false
    })
    btn.addEventListener("mouseleave", delay(e => {
        if (btn.isMouseOver !== true) {
            if (btn.children.length > 1) {
                toggleDropdown(parentItem, btn, products, displayedProduct);
            }
        }
    }, 700))
    node.appendChild(btn)
    return node
}

function toggleDropdown(parentItem, dropdownBtn, products, displayedProduct) {
    if (dropdownBtn.children.length > 1) {
        clearNodeChildren(dropdownBtn);
        let arrow = createCustomElement("div", defs.dropdownArrow, defs.dropdownDownArrow);
        dropdownBtn.appendChild(arrow);
    } else {
        clearNodeChildren(dropdownBtn);
        let arrow = createCustomElement("div", defs.dropdownArrow, defs.dropdownUpArrow);
       
        dropdownBtn.appendChild(arrow);
        let items = buildDropdownItems(parentItem, products, displayedProduct);
        dropdownBtn.appendChild(items);
    }

}

function buildDropdownItems(parentItem, products, displayedProduct) {
    let items = createCustomElement("ul", defs.dropdownList, defs.verticalList);
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

            let li = createCustomElement("li", defs.dropdownItem);
            let btn = document.createElement("button");
            btn.innerText = priceStr + nameStr;
            btn.addEventListener("click", event => {
                refreshPage(parentItem, ordered[i]);
            })
            li.appendChild(btn);
            items.appendChild(li)
        }
    }
    return items
}