<script setup lang="ts">
import { ref, watch } from "vue";
import type { Ref } from "vue";

import { useDetectClickElement } from "@/composables";

const props = defineProps<{
    placeholder: string,
    results: {id: number, name: string}[],
}>();

const emit = defineEmits<{
    input: [query: string],
    select: [select: {id: number, name: string}]
}>();

let dropdownIsToggled = ref(false);
let dropdownIsEnabled = ref(false);
let previousQuery: Ref<string | null> = ref(null);
let timer = ref(0); // for SetTimeout()
let containerElement: Ref<HTMLElement | null> = ref(null)

function handleUserInput(event: Event): void {
    clearTimeout(timer.value);
    timer.value = setTimeout(() => {
        let value = (event.target as HTMLInputElement).value.trim();
        if (value !== "") {
            if (value !== previousQuery.value) {
                previousQuery.value = value;
                emit("input", value)
                dropdownIsEnabled.value = true;

            } else {
                // Here we simply show the result of the previous query
                if (previousQuery.value !== null) {
                    dropdownIsEnabled.value = true;
                }
            }
        } else {
            // Disable dropdown when input field is clear
            dropdownIsEnabled.value = false;
        }
    }, 600)
};

function handleItemSelect(item: {id: number, name: string}): void {
    emit("select", item)
    // Note that this does not mutate results, just disables the dropdown
    dropdownIsEnabled.value = false;
};

function updateDropdownState(setState: boolean): void {
    dropdownIsToggled.value = setState;
};

// Watcher that enables the dropdown if results: (A: is mutated and B: has length more than 0)
watch(props.results, () => {
    if (props.results.length > 0) {
        dropdownIsEnabled.value = true;
    } else {
        dropdownIsEnabled.value = false;
    };
});

/*
Since I had to create a mouse click handler:
both the equivalent to "@focus" and "@blur" are handled here
The difference is that the click event is checked on the container <div> instead of the <input>
*/
useDetectClickElement(containerElement, updateDropdownState)
</script>

<template>
    <div class="container" ref="containerElement">
        <input class="field" :placeholder="placeholder" @input="handleUserInput"/>
        <ul class="dropdown" v-show="dropdownIsEnabled && dropdownIsToggled">
            <li class="item" v-for="item in props.results" :key="item.id">
                <button class="button" @click="handleItemSelect(item)">
                    {{ item.name }}
                </button>
            </li>
        </ul>
    </div>
</template>

<style scoped lang="css">
    .container {
        display: flex;
        flex-flow: column;
        width: 24rem;
        align-items: center;
    }

    .field {
        border: 0;
        outline: 0;
        border-radius: 1.5rem;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        height: 2.5rem;
        width: 19.6rem;
        margin-top: 0.2rem;
        color: var(--clr-text);
        background-color: var(--grey-100);
        z-index: 2;
        box-shadow: inset 0 1px 3px hsla(0, 0%, 0%, 0.4), 0 1px 0 hsl(210, 30%, 90%)
    }

    .field:hover {
        background-color: var(--primary-light-200);
    }

    .field:focus::placeholder {
        color: transparent;
    }

    .dropdown {
        position: absolute;
        list-style: none;
        padding: 0;
        border-radius: 1.5rem;
        width: 20rem;
        z-index: 1;
        padding: 0.2rem;
        padding-top: 2.9rem;
        background-color: var(--grey-200);
        box-shadow: inset 0 1px 0 hsl(210, 30%, 97%), 0 1px 3px hsla(0, 0%, 0%, 0.4)
    }

    .item {
        display: flex;
        flex-direction: row;
    }

    .button {
        width: 100%;
        padding: 0.4rem 0.8rem;
        font-size: 1.1rem;
        font-weight: bold;
        font-style: oblique;
        text-align: center;
        color: var(--grey-700);
        background-color: var(--grey-200);
        border: 0;
    }

    .button:hover {
        background-color: var(--primary-light-200);
    }

    /* Round the bottom border of the last element in the list */
    .dropdown .item:last-child .button {
        border-radius: 0 0 1.5rem 1.5rem;
    }

</style>