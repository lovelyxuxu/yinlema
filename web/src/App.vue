<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute, useRouter, RouterView } from "vue-router";
import AppTopBar from "./components/AppTopBar.vue";
import BottomNav from "./components/BottomNav.vue";
import { useAuth } from "./stores/auth";
import { initIdentityFromServer } from "./stores/identity";
import { useRecords } from "./stores/records";

const route = useRoute();
const router = useRouter();
const { fetchMe, user, isLoggedIn, logout } = useAuth();
const { fetchRecords } = useRecords();

const showShell = computed(() => route.name !== "auth");

const pageTitle = computed(() => {
  const t = route.meta.title;
  if (typeof t === "string" && t) return t;
  if (route.path.startsWith("/social")) return "社交";
  return "鹿了么";
});

function handleLogout() {
  logout();
  router.push("/auth");
}

onMounted(async () => {
  if (!isLoggedIn.value) return;

  const ok = await fetchMe();
  if (!ok) return;

  if (user.value?.identity_role) {
    initIdentityFromServer(user.value.identity_role);
  }

  fetchRecords().catch(() => {});
});
</script>

<template>
  <div class="app-shell">
    <AppTopBar v-if="showShell" :title="pageTitle">
      <template #trailing>
        <button type="button" class="logout-btn" @click="handleLogout">退出</button>
      </template>
    </AppTopBar>
    <main class="app-main" :class="{ 'with-topbar': showShell }">
      <RouterView />
    </main>
    <BottomNav v-if="showShell" />
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

.app-main.with-topbar {
  padding-top: calc(var(--app-topbar-h) + var(--safe-top, 0px) + 8px);
}

.logout-btn {
  background: none;
  border: 1px solid var(--card-border);
  color: var(--muted);
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 999px;
  transition: color 0.15s, border-color 0.15s;
}

.logout-btn:hover {
  color: var(--text);
  border-color: rgba(0, 0, 0, 0.20);
}
</style>
