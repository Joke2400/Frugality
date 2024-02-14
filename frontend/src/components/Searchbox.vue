<script setup lang="ts">
import { ref } from "vue"

const props = defineProps({
    placeholder: String,
    items: Array
});
const emit = defineEmits({"input-event": String});
let timer = ref(0);

function handleInput(event: Event): void {
    clearTimeout(timer.value);
    timer.value = setTimeout(() => {
        if (event.target instanceof HTMLInputElement) {
            if (event.target.value !== "") {
                emit("input-event", event.target.value);
            };
        }
    }, 600);
}

</script>

<template>
    <div class="search-box">
        <input class="field" :placeholder="placeholder" @input="handleInput" />
    </div>
</template>



<style scoped>

    .search-box {
        background-color: var(--clr-debug-red);
    }
    .field {
        border: 0;
        border-radius: 1rem;
        padding: 0.4rem 0.8rem;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px 5px rgba(0, 0, 0, 0.3);
        font-weight: bold;
        text-align: center;
        background-color: var(--clr-background-light);
    }
    
    .field:hover {
        background-color: var(--clr-foreground-light);
    }

    .field:focus {
        outline: 0.05rem solid var(--secondary-text-dark);
    }

    .field:focus::placeholder {
        color: transparent;
    }

</style>