<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { useRoute } from "vue-router";

const route = useRoute();

const tabs = [
  { to: "/social/rank", label: "排名" },
  { to: "/social/plaza", label: "七嘴八舌" },
  { to: "/social/teams", label: "小组" },
];

function tabActive(path: string) {
  return route.path === path;
}
</script>

<template>
  <div class="social-shell">
    <div class="subnav">
      <RouterLink
        v-for="t in tabs"
        :key="t.to"
        :to="t.to"
        class="pill"
        :class="{ active: tabActive(t.to) }"
      >
        {{ t.label }}
      </RouterLink>
    </div>
    <RouterView />
  </div>
</template>

<style scoped>
.social-shell {
  min-height: 100%;
  padding: 8px 12px calc(92px + var(--safe-bottom, 0));
  max-width: 560px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.subnav {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
}
.subnav::-webkit-scrollbar {
  display: none;
}
.pill {
  flex: 1;
  min-width: 0;
  text-align: center;
  padding: 9px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 700;
  text-decoration: none;
  border: 1px solid var(--card-border);
  color: var(--muted);
  background: rgba(0, 0, 0, 0.04);
  transition:
    background 0.18s ease,
    color 0.18s ease,
    border-color 0.18s ease;
}
.pill.active {
  color: var(--text);
  border-color: rgba(2, 132, 199, 0.42);
  background: rgba(2, 132, 199, 0.10);
}
.pill:active {
  transform: scale(0.98);
}
</style>
