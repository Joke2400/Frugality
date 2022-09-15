document.addEventListener("DOMContentLoaded", function() {
    getRecipes();
  });
  
function getRecipes() {
    fetch("/recipes/fetch/")
    .then(response => response.json())
	.then(data => {
        var recipes = data["data"];
        var listElements = document.getElementsByClassName("recipe-button");
        for(var i = 0; i < recipes.length; i++) {
            let recipeName = recipes[i]["name"];
            let orderNum = i;
            if (i < listElements.length) {
                listElements[i].children[0].innerHTML = orderNum;
                listElements[i].children[1].innerHTML = recipeName;
            } else {if (i >= listElements.length) {
                addRecipeElement(recipeName, orderNum);
            }}
        }
    })

}

function addRecipeElement(recipeName, orderNum) {
    let list = document.getElementsByClassName("recipe-list")[0];
    let last = list.children[list.children.length -1];

    let newElement = document.createElement("li");
    let div = document.createElement("div");
    div.className = "recipe-div";
    
    let button = document.createElement("button")
    button.className = "recipe-button";
    button.onclick = function () {
        viewIngredients(recipeName);
    };
    let header = document.createElement("h4");
    header.innerHTML = orderNum;
    let paragraph = document.createElement("p");
    paragraph.innerHTML = recipeName;
    
    button.appendChild(header);
    button.appendChild(paragraph);
    div.appendChild(button);
    newElement.appendChild(div);
    list.insertBefore(newElement, last);
}

function viewIngredients(recipeName) {
    console.log(recipeName);
};









function createRecipeDisplay() {
    var containerElement = document.getElementsByClassName("container")[0]
    var new_style = `
        height: 150vh;
        grid-template-areas:
        "nav nav nav"
        "content-large content-large sidebar"
        "content-large content-large sidebar"
        "create-recipe create-recipe sidebar"
        "footer footer footer";
        grid-template-rows: 3em 4em 1fr 0.7fr 5em;
        
    `;
    containerElement.style.cssText = new_style
    var recipe_div = document.createElement("div")
    recipe_div.className = "create-recipe"
    var footer = document.getElementsByClassName("footer")[0]
    containerElement.insertBefore(recipe_div, footer)
}






function createRecipe() {
    var elements = document.getElementsByClassName("ingredient");
    var ingredients = []
    for(var i = 0; i < elements.length; i++) {
        let name = elements[i].name
        let amount = elements[i].amount
        ingredients.push({name: name, amount: amount})
    }
    var fetchData = {
        method: "post",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            operation: "create_recipe",
            ingredients: ingredients
        })
    }
    fetch("/new_recipe/", fetchData)
}