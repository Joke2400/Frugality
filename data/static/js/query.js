
function sendQuery() {
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            operation: document.getElementById("operation").value,
            store_id: document.getElementById("store_id").value,
            query: document.getElementById("query").value,
            category: document.getElementById("category").value     
        })
    }
    fetch("/query/", fetchData).then(response => response.json())
    .then(function(data) {
        document.getElementById("response_embed").innerHTML = data["data"];
    });
}