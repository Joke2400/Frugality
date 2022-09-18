function sendQuery() {
    let queries = [];
    let amounts = [];
    let categories = [];
    document.querySelectorAll(".query_field").forEach(r => queries.push(r.value));
    document.querySelectorAll(".amount_field").forEach(r => amounts.push(r.value));
    document.querySelectorAll(".categories_select").forEach(r => categories.push(r.value));

    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            operation: document.getElementById("operation").value,
            store_id: document.getElementById("store_id").value,
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