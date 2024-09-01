<script setup lang="ts">

</script>

<template>
    <header class="overview shadow-medium">
        <div class="overview-box">
            <h2>THIS MONTH</h2>
            <div class="horizontal-flex">
                <h3>+4.5%</h3>
                <p>Price Change</p>
            </div>

        </div>
        <div class="overview-box">
            <h2>REFERENCE BASKET</h2>
            <div class="horizontal-flex">
                <h3>+3.3%</h3>
                <p>Price Change</p>
            </div>

        </div>
        <div class="overview-box">
            <h2>CURRENTLY TRACKING</h2>
            <div class="vertical-box">
                <div class="horizontal-flex">
                    <h3>1328</h3>
                    <p>Products</p>
                </div>
                <div class="horizontal-flex">
                    <h3>43</h3>
                    <p>Stores</p>
                </div>
            </div>
        </div>
    </header>
</template>

<style scoped lang="css">
    h2 {
        opacity: 90%;
        font-size: 1.5rem;
        font-weight: bold;
        font-family: "Sora";
        color: var(--primary-light-300);
    }

    h3 {
        margin-right: 0.5rem;
        opacity: 90%;
        font-size: 1.25rem;
        line-height: 2;
        font-family: "Sora";
        color: var(--grey-200);
    }

    p {
        opacity: 90%;
        font-size: 1.25rem;
        line-height: 2;
        font-weight: bold;
        font-family: "Sora";
        color: var(--grey-200);
    }

    .overview {
        width: 100%;
        height: 30vh;
        min-height: 12rem;
        margin-top: 7vh;
        padding-left: 3vw;
        padding-right: 3vw;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        overflow: hidden;
        background: linear-gradient(to bottom right, var(--primary-light-900), var(--primary-light-600));
    }

    .overview-box {
        margin-top: 5vh;
        display: flex;
        flex-direction: column;
    }

    .horizontal-flex {
        display: flex;
        flex-direction: row;
    }

    .vertical-flex {
        display: flex;
        flex-direction: column;
    }

    .details-btn {
        margin-top: auto;
        margin-bottom: 6vh;
        opacity: 90%;
        padding: 0.25rem 0.5rem 0.25rem 0.5rem;
        border: 0;
        border-radius: 0.25rem;
        font-size: 1.125rem;
        width: fit-content;
        font-family: "Noto Sans";
        color: var(--grey-100);
        background-color: var(--primary-light-700);
        box-shadow: inset 0 1px 0 hsl(210, 50%, 80%), 0 3px 5px hsla(0, 0%, 0%, 0.2)
    }

    .details-btn:hover {
        background-color: var(--primary-light-600);
    }
</style>