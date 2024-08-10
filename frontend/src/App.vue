<script setup lang="ts">
import type { Ref } from 'vue';
import { ref } from "vue";

import type { StoreResponse } from "./data";
import { Store } from "./data";
import { post } from "./utils";

import InputField from "./components/InputField.vue";

// temporarily defined here cause im lazy
let apiHost = "http://localhost:8081";


let selectedStores: Ref<Store[]> = ref([]);
let currentStores: Ref<Store[]> = ref([]);
let dropdownStores: Ref<{id: number, name: string}[]> = ref([])

async function updateStores(query: string): Promise<void> {
    console.log(`Fetching stores for query: ${query}`);
    let params: {[key: string]: any} = {store_id: null, store_name: null}
    let i = parseInt(query);
    if (isNaN(i)) {
        params.store_name = query;
    } else {
        params.store_id = i;
    }
    await post(apiHost + '/stores/', params)
    .then(async response => await response.json() as Promise<StoreResponse>)
    .then(parsed => {
        currentStores.value = parsed.results.map(({store_id, store_name, slug, brand}) => (
            new Store(store_id, store_name, slug, brand)));
        // Here we provide new values for the input dropdown
        dropdownStores.value = currentStores.value.map(store => (store.getIdentifiers()))
        console.log("currentStores:", currentStores.value)
        console.log("dropdownStores:", dropdownStores.value)
    })
    .catch(err => {console.log(err)})
}

function selectStore(store: {id: number, name: string}): void {
    /*
    if (!selectedStores.value.includes(store)) {
        selectedStores.value.push(store)
    }
    */
}
</script>


<template>
    <nav class="shadow-medium">
        <h1 style="font-weight: bold;">Frugality</h1>
    </nav>
    <div class="overview">
        <div class="placeholders">
            <button style="background-color: var(--primary-light-100)"></button>
            <button style="background-color: var(--primary-light-200)"></button>
            <button style="background-color: var(--primary-light-300)"></button>
            <button style="background-color: var(--primary-light-400)"></button>
            <button style="background-color: var(--primary-light-500)"></button>
            <button style="background-color: var(--primary-light-600)"></button>
            <button style="background-color: var(--primary-light-700)"></button>
            <button style="background-color: var(--primary-light-800)"></button>
            <button style="background-color: var(--primary-light-900)"></button>

            <button style="background-color: var(--grey-100)"></button>
            <button style="background-color: var(--grey-200)"></button>
            <button style="background-color: var(--grey-300)"></button>
            <button style="background-color: var(--grey-400)"></button>
            <button style="background-color: var(--grey-500)"></button>
            <button style="background-color: var(--grey-600)"></button>
            <button style="background-color: var(--grey-700)"></button>
            <button style="background-color: var(--grey-800)"></button>
            <button style="background-color: var(--grey-900)"></button>

            <button style="background-color: var(--red-500)"></button>
            <button style="background-color: var(--yellow-500)"></button>
            <button style="background-color: var(--green-500)"></button>
        </div>
    </div>
    <div class="main-content">
        <div class="input-fields">
            <InputField :placeholder="'Search for a store'" :results="dropdownStores" @input="updateStores" @select="selectStore"/>
            <ul v-if="selectedStores.length > 0">
                <li v-for="item in selectedStores" :key="item.storeId">
                    <p>{{ item.storeName }}</p>
                </li>
            </ul>
        </div>
        <div class="results">
        </div>
    </div>
</template>


<style scoped>
nav {
    position: fixed;
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 100%;
    height: 4rem;
    padding-left: 1rem;
    padding-right: 1rem;
    background-color: var(--grey-100);
}

.overview {
    width: 100%;
    height: 24rem;
    margin-top: 3rem;
    background-color: var(--primary-light-900);
}

.main-content {
    display: flex;
    flex-direction: row;
    height: 100%;
}

.input-fields {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
    padding-top: 3rem;
    background-color: var(--grey-100);
}

.results {
    display: flex;
    flex-direction: column;
    width: 70%;
    height: 100%;
    background-color: var(--grey-200);
}

.placeholders button {
    margin-top: 2rem;
    margin-left: 0.5rem;
    width: 3rem;
    height: 3rem;
    border: 0;
    box-shadow: 0 1px 3px hsla(0, 0%, 0%, .2);
}
</style>