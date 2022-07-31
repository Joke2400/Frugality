
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

let button = document.createElement("button")
new_element.className = "recipe-button"
let header = document.createElement("h4");
header.innerHTML = orderNum
let paragraph = document.createElement("p");
paragraph.innerHTML = recipeName

new_element.appendChild(button)
button.appendChild(header)
button.appendChild(paragraph)