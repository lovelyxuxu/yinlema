<script setup lang="ts">
import { onMounted } from "vue";
import { useRoute, RouterView } from "vue-router";
import BottomNav from "./components/BottomNav.vue";
import { useAuth } from "./stores/auth";
import { initIdentityFromServer } from "./stores/identity";
import { useRecords } from "./stores/records";

const route = useRoute();
const { fetchMe, user, isLoggedIn } = useAuth();
const { fetchRecords } = useRecords();

onMounted(async () => {
  if (!isLoggedIn.value) return;

  const ok = await fetchMe();
  if (!ok) return;

  // 用服务端角色覆盖本地
  if (user.value?.identity_role) {
    initIdentityFromServer(user.value.identity_role);
  }

  // 预加载记录（HomeRecords 内也会调用，有缓存保护）
  fetchRecords().catch(() => {});
});
</script>

<template>
  <div class="app-shell">
    <main class="app-main">
      <RouterView />
    </main>
    <BottomNav v-if="route.name !== 'auth'" />
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
