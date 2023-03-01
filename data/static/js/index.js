
function sendQuery() {
    let queries = [];
    let amounts = [];
    let categories = [];
    document.querySelectorAll(".item_name").forEach(r => queries.push(r.innerText));
    document.querySelectorAll(".item_amount").forEach(r => amounts.push(r.innerText));
    document.querySelectorAll(".item_category").forEach(r => categories.push(r.innerText));
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            queries: queries,
            amounts: amounts,
            categories: categories
        })
    }
    fetch("/query/", fetchData);
}