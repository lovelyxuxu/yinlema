<script setup lang="ts">
import { useIdentity } from "../stores/identity";

const { roles, activeRole, setRole } = useIdentity();
</script>

<template>
  <div class="page">
    <header class="hero">
      <p class="eyebrow">身份</p>
      <h1>切换今日概率</h1>
      <p class="lead">
        影响「今日鹿么」里随机到「鹿」的概率。代码内用概率数值表示，界面仍使用「鹿」这一中文代称。
      </p>
    </header>

    <section class="list" role="list">
      <button
        v-for="role in roles"
        :key="role.id"
        type="button"
        class="role"
        :class="{ active: activeRole.id === role.id }"
        role="listitem"
        @click="setRole(role.id)"
      >
        <div class="role-head">
          <span class="role-name">{{ role.label }}</span>
          <span class="role-pill">鹿概率 {{ Math.round(role.luProbability * 100) }}%</span>
        </div>
        <p class="role-desc">{{ role.description }}</p>
      </button>
    </section>
  </div>
</template>

<style scoped>
.page {
  min-height: 100%;
  padding: 20px 16px 96px;
  max-width: 560px;
  margin: 0 auto;
}

.hero h1 {
  margin: 6px 0 10px;
  font-size: 24px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
  font-size: 14px;
}

.list {
  margin-top: 16px;
  display: grid;
  gap: 10px;
}

.role {
  width: 100%;
  text-align: left;
  border-radius: var(--radius-lg);
  padding: 14px 14px;
  background: var(--card);
  border: 1px solid var(--card-border);
  color: var(--text);
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    transform 0.05s ease;
}

.role:active {
  transform: translateY(1px);
}

.role.active {
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.18) inset;
}

.role-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.role-name {
  font-weight: 700;
}

.role-pill {
  font-size: 12px;
  color: var(--muted);
  border: 1px solid var(--card-border);
  padding: 4px 8px;
  border-radius: 999px;
}

.role-desc {
  margin: 8px 0 0;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}
</style>
