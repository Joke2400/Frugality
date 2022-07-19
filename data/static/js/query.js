
function sendQuery() {
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            operation: document.getElementById("operation").value,
            variables: document.getElementById("variables").value
        })
    }
    fetch("/query/", fetchData).then(response => response.json())
    .then(function(data) {
        document.getElementById("response_embed").innerHTML = data["data"];
    });
}

function createRecipe() {
    var elements = document.getElementsByClassName("ingredient");
    var ingredients = []
    for(var i = 0; i < elements.length; i++) {
        let name = elements[i].name
        let amount = elements[i].amount
        ingredients.push({name: name, amount: amount})
    }
    let fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            ingredients: ingredients
        })
    }
    fetch("/new_recipe/", fetchData)
}