function sendQuery() {
    let queries = [];
    let amounts = [];
    let categories = [];
    document.querySelectorAll(".query").forEach(r => queries.push(r.value));
    document.querySelectorAll(".amount").forEach(r => amounts.push(r.value));
    document.querySelectorAll(".categories").forEach(r => categories.push(r.value));
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            store: document.getElementById("store").value,
            queries: queries,
            amounts: amounts,
            categories: categories
        })
    }
    fetch("/query/", fetchData).then(response => response.json())
    .then(function(data) {
        document.getElementById("response_embed").innerHTML = JSON.stringify(data["data"]);
    });
}

var categories = [
    "",
    "hedelmat-ja-vihannekset-1",
    "leivat-keksit-ja-leivonnaiset-1",
    "liha-ja-kasviproteiinit-1",
    "kala-ja-merenelavat-1",
    "maito-munat-ja-rasvat-0",
    "juustot-0"
];

var categoryStrings = [
    "Select category",
    "Hedelmät ja vihannekset",
    "Leivät, keksit ja leivonnaiset",
    "Liha ja kasviproteiinit",
    "Kala ja merenelävät",
    "Maito, munat ja rasvat",
    "Juustot"
];

addEventListener('DOMContentLoaded', _ => {
    cat_selects = document.querySelectorAll(".categories").forEach(r => {
        for (let i = 0; i< categories.length; i++) {
            let s = document.createElement("option");
            s.setAttribute("value", categories[i]);
            s.innerText = categoryStrings[i];
            r.append(s);
        }
    })
});