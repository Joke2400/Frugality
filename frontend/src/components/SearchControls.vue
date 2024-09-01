<script setup lang="ts">
import type { Ref } from 'vue';
import { ref } from "vue";

import type { StoreResponse, ProductResponse } from "@/data";
import { Store, Product } from "@/data";
import { post } from "@/utils";

import InputField from "./InputField.vue";

// temporarily defined here cause i'm lazy
let apiHost = "http://localhost:8081";

const storeQueries = defineModel<Store[]>(
    "storeQueries", { required: true });
const productQueries = defineModel(
    "productQueries", { required: true });

let storesSearchResult: Ref<Store[]> = ref([]);
let storesDropdownProp: Ref<{ id: number, name: string }[]> = ref([]);


/**
 * Search for a store using the provided query string.
 * 
 * @param {string} query - The query string to be used in the search.
 * @returns {Promise<void>} - A Promise that resolves after the search is done.
 */
async function storeSearch(query: string): Promise<void> {
    let params: { [key: string]: any } = { store_id: null, store_name: null }
    let i = parseInt(query);
    if (isNaN(i)) {
        params.store_name = query;
    } else {
        params.store_id = i;
    }
    await post(apiHost + '/stores/', params)
        .then(async response => await response.json() as Promise<StoreResponse>)
        .then(parsed => {
            storesSearchResult.value = parsed.results
                .map(({ store_id, store_name, slug, brand }) => (
                    new Store(store_id, store_name, slug, brand)));
            // Here we provide new values for the input dropdown
            storesDropdownProp.value = storesSearchResult.value.map(
                store => (store.getIdentifiers()))
        })
        .catch(err => { console.log(err) })
}

async function productSearch(): Promise<void> { }

function handleStoreSelect(storeId: number): void {
    const store = storesSearchResult.value.find(obj => obj.storeId == storeId)
    if (store !== undefined) {
        if (!storeQueries.value.includes(store)) {
            storeQueries.value.push(store)
        }
    }
}

function handleProductEntry(): void { }

</script>

<template>
    <aside class="container">
        <div class="store-fields">
            <InputField :placeholder="'Search for a store'" :results="storesDropdownProp" @input="storeSearch"
                @select="handleStoreSelect" />
        </div>
        <div class="product-fields">
            <InputField :placeholder="'Search for a product'" :results="[]" />
        </div>
    </aside>
</template>

<style scoped lang="css">
.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 20%;
    max-width: 30rem;
    min-width: 20rem;
    background-color: var(--grey-100);
}

.store-fields {
    width: 100%;
    height: 10rem;
    padding-top: 2rem;
    z-index: 2;
    background-color: var(--debug-yellow);
}

.product-fields {
    background-color: var(--debug-blue);
    width: 100%;
    height: 10rem;
    padding-top: 2rem;
    z-index: 1;
}
</style>