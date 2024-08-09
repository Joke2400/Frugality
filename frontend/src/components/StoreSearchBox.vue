<script setup lang="ts">
import type { Store, StoreQuery } from "../types"
import { ref, watch } from "vue"

const model = defineModel<Store[]>("searchResults");

const props = defineProps<{
    placeholder: string,
}>();

const emit = defineEmits<{
    input: [query: StoreQuery]
    select: [store: Store]
}>();

let timer = ref(0);
let isActive = ref(false)

function handleInput(event: Event): void {
    clearTimeout(timer.value);
    timer.value = setTimeout(() => {
        let e = event.target as HTMLInputElement
        if (e.value !== "") {
            let value = e.value.trim()
            let i = parseInt(value);
            if (isNaN(i)) {
                emit("input", {storeId: null, storeName: e.value});
            } else {
                emit("input", {storeId: i, storeName: null});
            };
        } else {
            model.value = [];
        }
    }, 600);
};

function handleSelect(item: Store): void {
    emit("select", item)
    model.value = [];
}

watch(model, async() => {
    let value = model.value as Store[]
    if (value.length > 0) {
        isActive.value = true;
    } else {
        isActive.value = false;
    }
})
</script>


<template>
    <div class="search-box">
        <input class="field" :class="{ active: isActive, shadow: !isActive}" :placeholder="placeholder" @input="handleInput" />
        <ul v-if="isActive" class="list">
            <li class="list-item" v-for="item in searchResults" :key="item.store_id">
                <button class="item-button" @click="handleSelect(item)">{{ item.store_name }}</button>
            </li>
        </ul>
    </div>
</template>


<style scoped>
    .search-box {
        display: flex;
        flex-flow: column;
        width: 20rem;
    }

    .field {
        border: 0;
        border-radius: 1rem;
        padding: 0.4rem 0.8rem;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        height: 2.5rem;
        background-color: var(--clr-background-light);
    }

    .field:hover {
        background-color: var(--clr-foreground-light);
    }

    .field:focus {
        outline: 0.05rem solid var(--clr-primary-light-200);
    }

    .field:focus::placeholder {
        color: transparent;
    }

    .active {
        border-radius: 1rem 1rem 0 0;
        outline: 0.05rem solid var(--clr-primary-light-200);
    }

    .list {
        position: absolute;
        list-style: none;
        padding: 0;
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        outline: 0.05rem solid var(--clr-primary-light-200);
        border-radius: 0 0 1rem 1rem;
        z-index: 1;
        margin-top: 2.5rem;
    }

    .list-item {
        display: flex;
        flex-direction: row;
        width: 20rem;
    }

    .item-button {
        width: 100%;
        padding: 0.4rem 0.8rem;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        color: var(--clr-primary-light-500);
        background-color: var(--clr-background-light);
        border: 0;
        border-bottom: 0.01rem solid var(--clr-primary-light-200);
    }

    .item-button:hover {
        background-color: var(--clr-foreground-light);
    }

    /* Round the bottom border of the last element in the result list */
    .list .list-item:last-child .item-button {
        border-radius: 0 0 1rem 1rem;
        border-bottom: 0;
    }

</style>