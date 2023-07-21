import { dom, domStyle, refreshChildren} from "./utils.js";

const main = document.getElementById("main");

window.onload = e => {
    window.results = JSON.parse(localStorage.getItem("results"));
    refreshChildren(main, results, buildResults);
};

function buildResults(results) {
    for (let i = 0; i < results.length; i++) {
        createResultsSection(results[i])
    }
};

function createResultsSection(store) {
    let section = document.createElement("section");
    section.classList.add(dom.storeSection, domStyle.shadow)
    let h3 = (e) => {
        var i = document.createElement(document.createElement("h3"))
        i.innerText = store[1]
        return i
    }
    section.appendChild(h3)
}

function createResultItem() {}



// li class="result-item"
// div class="product-data"
// div class="price-data"



// For store in result
    // Create section
        // Create header
        // Create query list
            // For each query result in queries
            // Append first result item to query list