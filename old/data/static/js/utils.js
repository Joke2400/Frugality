export { get, post, del, dom, domStyle, delay};
export { clearNodeChildren, appendToParentInOrder, refreshChildren}
export { createCustomElement, appendTextElement, appendParagraph, appendClassedParagraph }
export { appendH1Element, appendH2Element, appendH3Element, appendH4Element, appendH5Element, appendH6Element,}

// Keeping all the IDs and classes used in selectors/(element creation)
// in one place, there's better solutions but this is good for now
var dom = {
    storeBox: "store-box",
    storeInput: "store-input",
    storesList: "stores-list",
    storeContainer: "store-result-container",
    storeResult: "store-result-item",
    storeResultBtn: "store-result-btn",
    storeItem: "store-item",
    storeItemText: "store-item-txt",
    queryAddBtn: "query-add-btn",
    queryInput: "query-input",
    productsList: "products-list",
    productName: "product-name",
    productCategory: "product-category",
    productText: "product-text",
    productData: "product-data",
    productItem: "product-item",
    btn: "btn",
    sendQueryBtn: "send-query-btn",
    storeSection: "store-result",
    resultItem: "result-item",
    productData: "product-data",
    priceData: "price-data",
    verticalList: "vertical-list",
    resultsList: "results-list",
    count: "count",
    storeHeader: "store-header",
    originalQuery: "orig-query",
    dropdownBtn: "dropdown-btn",
    dropdown: "dropdown",
    dropdownItem: "dropdown-item",
    itemTotalBox: "item-total",
}   // This is getting so long it needs to be split/redone completely

var domStyle = {
    rounded: "rounded",
    roundedMore: "rounded-more",
    roundedTop: "rounded-top",
    roundedBottom: "rounded-bottom",
    borderBottomLight: "border-bottom-light",
    bottomShadow: "bottom-shadow",
    shadow: "shadow"
}


const request = (url, params, method) => {
    let options = {
        method,
    };
    if (method === "GET") {
        options.headers = {
            "Accept": "text/html, application/json"
        }
        if (params !== undefined) {
            url += '?' + (new URLSearchParams(params)).toString();
        }
    } else {
        options.body = JSON.stringify(params);
        options.headers = {
            "Accept": "text/html, application/json",
            "Content-Type": "application/json"}
    }
    return fetch(url, options);
};

const get = (url, params) => request(url, params, "GET");
const post = (url, params) => request(url, params, "POST");
const del = (url, params) => request(url, params, "DELETE");

function delay(fn, ms) {
    let timer = 0;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(fn.bind(this, ...args), ms || 0)
    }
}

function refreshChildren(listNode, items, fn) {
    clearNodeChildren(listNode);
    fn(items);
}

function clearNodeChildren(node) {
    while (node.lastElementChild) {
        node.removeChild(node.lastElementChild);
    }
}

function createCustomElement(type) {
    let element = document.createElement(arguments[0]);
    for (let i = 1; i < arguments.length; i++) {
        element.classList.add(arguments[i])
    }
    return element
}

function appendToParentInOrder(parent) {
    for (let i = 1; i < arguments.length; i++) {
        parent.appendChild(arguments[i]);
    }
}


// ---------------------------------------------------------
// Text element creation functions
// ---------------------------------------------------------
function appendTextElement(parent, type, text) {
    let paragraph = document.createElement(type);
    paragraph.innerText = text;
    parent.appendChild(paragraph);
}

function appendParagraph(parent, text) {
    appendTextElement(parent, "p", text)
}

function appendClassedParagraph(parent, text) {
    let element = document.createElement("p");
    for (let i = 2; i < arguments.length; i++) {
        element.classList.add(arguments[i])
    }
    element.innerText = text
    parent.append(element)
}

function appendH1Element(parent, text) {
    appendTextElement(parent, "h1", text)
}

function appendH2Element(parent, text) {
    appendTextElement(parent, "h2", text)
}

function appendH3Element(parent, text) {
    appendTextElement(parent, "h3", text)
}

function appendH4Element(parent, text) {
    appendTextElement(parent, "h4", text)
}

function appendH5Element(parent, text) {
    appendTextElement(parent, "h5", text)
}

function appendH6Element(parent, text) {
    appendTextElement(parent, "h6", text)
}
// ---------------------------------------------------------