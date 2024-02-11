<script setup lang="ts">

import  { ref } from 'vue'

let count = ref(0)

function incrementCounter(): void {
    count.value++
}

</script>


<template>
    <h1>Hello this is a test</h1>
    <p ref="counter">Counter: {{ count }}</p>
    <button @click="incrementCounter">
        <span>Increment</span>
    </button>
</template>


<script>

</script>


<style>
    h1 {
        color: red;
    }
</style>