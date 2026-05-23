<script setup lang="ts">
import { ref } from "vue";
import IdentityRoleCard from "../components/IdentityRoleCard.vue";
import { useIdentity } from "../stores/identity";

const { roles, activeRole, setRole } = useIdentity();
const settingRole = ref(false);

async function handleSetRole(id: Parameters<typeof setRole>[0]) {
  if (settingRole.value) return;
  settingRole.value = true;
  try {
    await setRole(id);
  } finally {
    settingRole.value = false;
  }
}
</script>

<template>
  <div class="page">
    <p class="page-intro lead">
      选择人设，影响「今日检定」里的瘾运。<br>
      当前身份：<strong class="active-label">{{ activeRole.label }}</strong>
    </p>

    <section class="list" role="list">
      <IdentityRoleCard
        v-for="role in roles"
        :key="role.id"
        :role="role"
        :active="activeRole.id === role.id"
        :disabled="settingRole"
        @select="handleSetRole(role.id)"
      />
    </section>

    <div class="impact-note">
      <svg class="note-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5" />
        <path d="M10 9v5M10 7v.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </svg>
      <p>人设仅影响今日检定的随机结果，不会写入记录。随时可以换。</p>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 16px 14px calc(108px + env(safe-area-inset-bottom, 0px));
  max-width: 560px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.page-intro {
  margin: 0 0 4px;
}

.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
  font-size: 14px;
}

.active-label {
  color: var(--accent-a);
  font-weight: 700;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.impact-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  border-radius: var(--radius-md);
  background: rgba(236, 72, 153, 0.06);
  border: 1px solid rgba(236, 72, 153, 0.14);
  padding: 12px 14px;
}

.note-icon {
  width: 18px;
  height: 18px;
  color: var(--accent-a);
  flex-shrink: 0;
  margin-top: 1px;
}

.impact-note p {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.6;
}
</style>
