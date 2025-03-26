<template>
  <div id="app">
    <router-view :key="$route.fullPath" />
  </div>
</template>

<script>
export default {
  name: "App"
};
</script>

<style>
/* Add global styles if needed */
</style>