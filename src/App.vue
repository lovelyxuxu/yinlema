<script setup lang="ts">
import { RouterView } from "vue-router";
import BottomNav from "./components/BottomNav.vue";
</script>

<template>
  <div class="app-shell">
    <main class="app-main">
      <RouterView />
    </main>
    <BottomNav />
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  min-height: 0;
  padding-bottom: 88px;
}
</style>
