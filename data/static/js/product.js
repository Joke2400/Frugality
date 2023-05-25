export { addProductQuery, productsList, buildProductQueries };
import { dom, domStyle, get, post, refreshList } from "./utils.js";

const productsList = document.querySelector("." + dom.productsList)

/* Adding and removing queries */
function addProductQuery(product) {
    if (!productQueries.includes(product)) {
        post("/product/query/select/",
            {product: product})
            .then(response => {
                if ("result" in response) {
                    if (response["result"] === true) {
                        productQueries.push(product);
                    }
                }
                console.log(`productQueries: [${productQueries}]`)
                refreshList(productsList, productQueries,
                    buildProductQueries);
            })
    }
}

function removeProductQuery() {}

/* Element creation functions */
function buildProductQueries(products) {
    for (let i = 0; i < products.length; i++) {
        let productItem = createProductItem(products[i]);
        productsList.appendChild(productItem);
    }
}


function createProductItem(values) {
    let [count, name, category] = values
    let productItem = document.createElement("div");
    productItem.classList.add(dom.productItem, domStyle.roundedMore, domStyle.shadow)
    productItem.appendChild(createProductDataElement(count, name, category));

    return productItem;
}

function createProductTextElement(productName, productCategory) {
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

function createProductDataElement(productCount, productName, productCategory) {
    let count = document.createElement("p");
    count.classList.add("count");
    count.innerText = productCount.toString() + "x";
    
    let btn = document.createElement("button");
    btn.classList.add(dom.btn, domStyle.roundedMore);
    btn.innerText = "-";
    btn.addEventListener("click", e => {
        removeProductQuery(productCount, productName, productCategory);
    });

    let productData = document.createElement("div");
    productData.classList.add(dom.productData)

    productData.appendChild(count);
    productData.appendChild(createProductTextElement(productName, productCategory));
    productData.appendChild(btn);
    
    return productData;
}