<template>
    <p style="color: var(--clr-primary-light-100)">placeholder1</p>
    <p style="color: var(--clr-primary-light-200)">placeholder2</p>
    <p style="color: var(--clr-primary-light-300)">placeholder3</p>
    <p style="color: var(--clr-primary-light-400)">placeholder4</p>
    <p style="color: var(--clr-primary-light-500)">placeholder5</p>
    <h1>Frugality</h1>
    <Searchbox :items="storeItems" placeholder="Search for a store" @input-event="sendStoreQuery"/>
</template>

<script setup lang="ts">
import Searchbox from "./components/Searchbox.vue"
import { get } from "./utils"

const baseURL = "http://localhost:8080"
let storeItems: [key: string][] = []

async function sendStoreQuery(query: string) {
    let s = `Sending query for: '${query}'`
    console.log(s)
    let json = await get(baseURL + "/stores/" + query)
    console.log(json)
}

</script>


<style scoped>
h1 {
    font-weight: bold;
}
</style>