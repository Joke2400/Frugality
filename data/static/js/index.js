import { storeQuery } from "./store.js";
import { delay, get} from "./utils.js";

var productQueries = [];

const addStoreBtn = document.getElementById("store_add_btn");
const addQueryBtn = document.getElementById("query_add_btn");

const storeInput = document.getElementById("store-input");
const storesList = document.querySelector(".stores-list");

//addStoreBtn.addEventListener("click", testFunc2);
//addQueryBtn.addEventListener("click", addProductQuery);
storeInput.addEventListener("input", delay(storeQuery, 1250))