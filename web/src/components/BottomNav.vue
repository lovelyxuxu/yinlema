<script setup lang="ts">
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();

const items = [
  { to: "/", label: "鹿了么", exact: true },
  { to: "/today", label: "今日鹿么" },
  { to: "/identity", label: "我是谁" },
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
      <!-- 鹿了么：柱状图图标 -->
      <svg v-if="item.to === '/'" class="nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="14" width="4" height="7" rx="1.5" fill="currentColor" opacity="0.5"/>
        <rect x="10" y="9" width="4" height="12" rx="1.5" fill="currentColor" opacity="0.75"/>
        <rect x="17" y="4" width="4" height="17" rx="1.5" fill="currentColor"/>
      </svg>
      <!-- 今日鹿么：骰子图标 -->
      <svg v-else-if="item.to === '/today'" class="nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="1.8"/>
        <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
        <circle cx="15.5" cy="8.5" r="1.5" fill="currentColor"/>
        <circle cx="8.5" cy="15.5" r="1.5" fill="currentColor"/>
        <circle cx="15.5" cy="15.5" r="1.5" fill="currentColor"/>
        <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
      </svg>
      <!-- 身份：盾牌图标 -->
      <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 3L4 6.5V11c0 4.5 3.5 8.5 8 9.5 4.5-1 8-5 8-9.5V6.5L12 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
        <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>{{ item.label }}</span>
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
  padding: 8px 8px calc(8px + var(--safe-bottom));
  background: rgba(7, 10, 15, 0.88);
  backdrop-filter: blur(16px) saturate(1.4);
  -webkit-backdrop-filter: blur(16px) saturate(1.4);
  border-top: 1px solid var(--card-border);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 4px 6px;
  border-radius: var(--radius-md);
  color: var(--muted);
  text-decoration: none;
  font-size: 11px;
  font-weight: 600;
  transition:
    color 0.18s ease,
    background 0.18s ease;
}

.nav-icon {
  width: 22px;
  height: 22px;
  transition: transform 0.18s ease;
}

.nav-item.active {
  color: var(--text);
  background: rgba(56, 189, 248, 0.1);
}

.nav-item.active .nav-icon {
  color: var(--accent-b);
  filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.5));
  transform: translateY(-1px);
}

.nav-item:active .nav-icon {
  transform: scale(0.9);
}
</style>
