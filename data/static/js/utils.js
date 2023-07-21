export { delay, refreshChildren, get, post, del, dom, domStyle };


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
    storeSection: "store-result"
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