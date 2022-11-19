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