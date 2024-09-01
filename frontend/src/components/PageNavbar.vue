<script setup lang="ts">

</script>

<template>
    <nav class="container shadow-medium">
        <h1 class="page-title">Frugality.</h1>
        <div class="links-box">
            <button class="link">Statistics</button>
            <button class="link">About</button>
        </div>
        <div class="lang-box">
            <h2 class="lang-text">EN</h2>
            <button class="lang-select material-symbols-outlined">language</button>
        </div>
    </nav>
</template>

<style scoped lang="css">
.container {
    width: 100%;
    min-height: 3rem;
    height: 7vh;
    padding-left: 3vw;
    padding-right: 3vw;
    z-index: 100;
    position: fixed;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    overflow: hidden;
    background-color: var(--grey-100);
}

.page-title {
    font-size: 2.25rem;
    letter-spacing: -0.05rem;
    font-family: "Sora";
    font-weight: 1000;
    color: var(--primary-light-700);
}

.links-box {
    gap: 3vw;
    height: 100%;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    width: fit-content;
}

.link {
    border: 0;
    min-width: 6vw;
    height: 100%;
    font-size: 1.25rem;
    padding-top: 0.3rem;
    letter-spacing: -0.05rem;
    font-weight: bold;
    font-family: "Noto Sans";
    color: var(--grey-800);
    background-color: var(--grey-100);
}

.link:hover {
    background-color: var(--primary-light-200);
}

.lang-box {
    height: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
}

.lang-text {
    margin-right: 0.5rem;
    font-size: 1.5rem;
    line-height: 1;
    letter-spacing: -0.05rem;
    font-family: "Noto Sans";
    font-weight: bold;
    color: var(--primary-light-700);
}

.lang-select {
    border: 0;
    padding: 0.5rem;
    color: var(--grey-300);
    background-color: var(--primary-light-700);
    box-shadow: inset 0 1px 0 hsl(210, 60%, 97%), 0 3px 5px hsla(0, 0%, 0%, 0.2)
}

.lang-select:hover {
    background-color: var(--primary-light-600);
}
</style>