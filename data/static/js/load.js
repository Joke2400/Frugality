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
            s = document.createElement("option");
            s.setAttribute("value", categories[i]);
            s.innerText = categoryStrings[i];
            r.append(s);
        }
    })
});