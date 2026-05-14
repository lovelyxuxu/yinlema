<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();

const items = [
  { to: "/", label: "鹿了么", exact: true },
  { to: "/today", label: "今日鹿么" },
  { to: "/identity", label: "身份" },
];

function isActive(path: string, exact?: boolean) {
  if (exact) return route.path === path;
  return route.path.startsWith(path);
}
</script>

<template>
  <nav class="nav" aria-label="主导航">
    <RouterLink
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="nav-item"
      :class="{ active: isActive(item.to, item.exact) }"
    >
      {{ item.label }}
    </RouterLink>
  </nav>
</template>

<style scoped>
.nav {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 10px 12px calc(10px + var(--safe-bottom));
  background: rgba(7, 10, 15, 0.86);
  backdrop-filter: blur(12px);
  border-top: 1px solid var(--card-border);
}

.nav-item {
  text-align: center;
  padding: 10px 8px;
  border-radius: var(--radius-md);
  color: var(--muted);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  transition:
    color 0.15s ease,
    background 0.15s ease;
}

.nav-item.active {
  color: var(--text);
  background: rgba(56, 189, 248, 0.12);
  box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.22);
}
</style>
