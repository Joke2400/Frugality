export { addProductQuery, productsList, buildProductQueries };
import { dom, domStyle, get, post, del, refreshChildren } from "./utils.js";

const sendQueryBtn = document.getElementById(dom.sendQueryBtn)
const addQueryBtn = document.getElementById(dom.queryAddBtn);
const productsList = document.querySelector("." + dom.productsList)

sendQueryBtn.addEventListener("click", event => {
    get("/product/query/").then(response => response.json())
    .then(response => {
        localStorage.setItem("results", JSON.stringify(response["results"]));
        window.location = response["url"];
    })
})

addQueryBtn.addEventListener("click", event => {
    let name = document.getElementById(dom.queryInput).value;
    if (name !== "") {
        let product = {
            query: name,
            count: 1,
            category: "",
        }
        addProductQuery(product);
    }
});


/* Adding and removing queries */
function addProductQuery(product) {
    post("/product/query/select/",
        {product: product}).then(response => response.json())
        .then(response => {
            if ("result" in response) {
                productQueries = response["result"];
            }
            console.log(`productQueries: [${productQueries}]`)
            refreshChildren(productsList, productQueries,
                buildProductQueries);
        })
}

function removeProductQuery(product) {
    del("/product/query/select",
        {category: product["category"],
         count: product["count"],
         quantity: product["quantity"],
         query: product["query"],
         slug: product["slug"],
         unit: product["unit"]}).then(response => response.json())
        .then(response => {
            if ("result" in response) {
                productQueries = response["result"];
            }
            console.log(`productQueries: [${productQueries}]`)
            refreshChildren(productsList, productQueries,
                buildProductQueries);
        })
}

/* Element creation functions */
function buildProductQueries(products) {
    for (let i = 0; i < products.length; i++) {
        let productItem = createProductItem(products[i]);
        productsList.appendChild(productItem);
    }
}


function createProductItem(product) {
    let productItem = document.createElement("div");
    productItem.classList.add(dom.productItem, domStyle.roundedMore, domStyle.shadow)
    productItem.appendChild(createProductDataElement(product));

    return productItem;
}

function createProductTextElement(productName, productCategory, productQuantity, productUnit) {
    let name = document.createElement("p");
    let category = document.createElement("p");
    name.classList.add(dom.productName);
    category.classList.add(dom.productCategory);
    name.innerText = productName;
    category.innerText = productCategory;

    let div = document.createElement("div");
    div.classList.add(dom.productText);
    div.appendChild(name);
    div.appendChild(category);
    return div;
}

function createProductDataElement(product) {
    let productName = product["query"];
    let productCount = product["count"];
    let productCategory = product["category"];
    let productQuantity = product["quantity"];
    let productUnit = product["unit"];
    let count = document.createElement("p");
    count.classList.add("count");
    count.innerText = productCount.toString() + "x";
    
    let btn = document.createElement("button");
    btn.classList.add(dom.btn, domStyle.roundedMore);
    btn.innerText = "-";
    btn.addEventListener("click", e => {
        removeProductQuery(product);
    });

    let productData = document.createElement("div");
    productData.classList.add(dom.productData)

    productData.appendChild(count);
    productData.appendChild(createProductTextElement(
        productName,
        productCategory,
        productQuantity,
        productUnit));
    productData.appendChild(btn);
    
    return productData;
}