export { delay, refreshList, get, post, getCookie };

const request = (url, params, method) => {
    let options = {
        method,
    };
    if (method === "GET") {
        options.headers = {
            "Accept": "application/json"
        }
        if (params !== undefined) {
            url += '?' + (new URLSearchParams(params)).toString();
        }
    } else {
        options.body = JSON.stringify(params);
        options.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"}
    }
    return fetch(url, options).then(response => response.json());
};

const get = (url, params) => request(url, params, "GET");
const post = (url, params) => request(url, params, "POST");

function getCookie() {
    document.cookie
    console.log(document.cookie)
}

function delay(fn, ms) {
    let timer = 0;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(fn.bind(this, ...args), ms || 0)
    }
}

function refreshList(listNode, items, fn) {
    clearNodeChildren(listNode);
    fn(items);
}

function clearNodeChildren(node) {
    while (node.lastElementChild) {
        node.removeChild(node.lastElementChild);
    }
}