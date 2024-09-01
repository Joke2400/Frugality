<script setup lang="ts">
import type { Ref } from 'vue';
import { ref } from "vue";

import { Store, Product } from "@/data";

import PageNavbar from './components/PageNavbar.vue';
import PageOverview from './components/PageOverview.vue';
import SearchControls from './components/SearchControls.vue';
import SearchResults from './components/SearchResults.vue';
import IntroStepper from './components/IntroStepper.vue';

let showResults: Ref<boolean> = ref(false)
let storeQueries: Ref<Store[]> = ref([])
let productQueries: Ref<Product[]> = ref([])

</script>

<template>
    <PageNavbar />
    <PageOverview />
    <div class="content">
        <SearchControls v-model:store-queries="storeQueries" v-model:product-queries="productQueries" />
        <SearchResults v-if="showResults" />
        <IntroStepper v-else />
    </div>
</template>

<style scoped>
.content {
    display: flex;
    flex-direction: row;
    height: 100%;
    width: 100%;
}
</style>