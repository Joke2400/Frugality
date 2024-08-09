<script setup lang="ts">
import type { Store, StoreResponse, StoreQuery, ProductQuery } from "./types"
import { post } from "./utils"
import SearchBox from "./components/StoreSearchBox.vue"
import type { Ref } from 'vue'
import { ref } from "vue"

// temp
let apiHost = "http://localhost:8081";

// This file will quickly become too long when updateProducts (etc) is implemented
// TODO SOLUTIONS: Do this within components ? Import functions from .ts file ? 
let selectedStores: Ref<Store[]> = ref([]);
let storeItems: Ref<Store[]> = ref([]);
let prevStoreItems: Ref<Store[]> = ref([]);
let prevStoreQuery: Ref<StoreQuery> = ref({storeId: null, storeName: null});

async function updateStores(query: StoreQuery): Promise<void> {
    if (JSON.stringify(query) === JSON.stringify(prevStoreQuery.value)) {
        storeItems.value = prevStoreItems.value;
        return
    }
    console.log(
        `Fetching stores for query: (${query.storeName} ${query.storeId})`
    );
    await post(apiHost + '/stores/', {
        store_id: query.storeId,
        store_name: query.storeName,
    })
    .then(async response => await response.json() as Promise<StoreResponse>)
    .then(parsed => {
        storeItems.value = parsed.results;
        prevStoreItems.value = parsed.results;
        prevStoreQuery.value = query;
    })
    .catch(err => {console.log(err)})
}

function selectStore(store: Store): void {
    if (!selectedStores.value.includes(store)) {
        selectedStores.value.push(store)
    }
}

async function updateProducts(query: ProductQuery) {}

</script>


<template>
    <nav class="shadow">
        <button class="nav-link">About</button>
    </nav>
    <div class="content">
        <div class="search-fields"></div>
        <h1 style="font-weight: bold;">Frugality</h1>
        <SearchBox v-model:searchResults="storeItems" placeholder="Search for a store" @input="updateStores" @select="selectStore"/>
        <ul v-if="selectedStores.length > 0">
            <li v-for="item in selectedStores" :key="item.store_id">
                <p>{{ item.store_name }}</p>
            </li>
        </ul>
        <p style="color: var(--clr-primary-light-100)">placeholder1</p>
        <p style="color: var(--clr-primary-light-200)">placeholder2</p>
        <p style="color: var(--clr-primary-light-300)">placeholder3</p>
        <p style="color: var(--clr-primary-light-400)">placeholder4</p>
        <p style="color: var(--clr-primary-light-500)">placeholder5</p>
    </div>
</template>


<style scoped>
.content {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-flow: column;
    height: 100vh;
}

.search-fields {

}
</style>