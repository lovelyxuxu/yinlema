<script setup lang="ts">
import type { IdentityRole } from "../stores/identity";
import { displayLuPercent, riverWidthPercent } from "../stores/identity";

defineProps<{
  role: IdentityRole;
  active: boolean;
  disabled?: boolean;
}>();

defineEmits<{ select: [] }>();
</script>

<template>
  <button
    type="button"
    class="role"
    :class="['lust-' + role.lustTier, { active }]"
    role="listitem"
    :disabled="disabled"
    @click="$emit('select')"
  >
    <div class="role-lust-bg" aria-hidden="true">
      <div class="lust-river" :style="{ width: riverWidthPercent(role) + '%' }" />
      <div class="lust-fog" />
      <div class="lust-tail" />
      <div class="lust-liquid" />
    </div>
    <div class="role-content">
      <div class="role-emoji" aria-hidden="true">{{ role.emoji }}</div>
      <div class="role-body">
        <div class="role-head">
          <span class="role-name">{{ role.label }}</span>
          <span class="role-pill" :class="{ 'pill-active': active }">
            瘾运 {{ displayLuPercent(role) }}
          </span>
        </div>
        <p class="role-desc">{{ role.description }}</p>
        <p class="role-flavor">{{ role.flavor }}</p>
      </div>
      <div v-if="active" class="check-mark" aria-hidden="true">
        <svg viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5" />
          <path
            d="M6.5 10.5l2.5 2.5 5-5"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </div>
    </div>
  </button>
</template>

<style scoped>
.role {
  width: 100%;
  text-align: left;
  border-radius: var(--radius-lg);
  padding: 14px;
  background: var(--card);
  border: 1px solid var(--card-border);
  color: var(--text);
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    background 0.18s ease,
    transform 0.08s ease;
  position: relative;
  overflow: hidden;
}

.role:active:not(:disabled) {
  transform: translateY(1px);
}

.role.active {
  border-color: rgba(236, 72, 153, 0.45);
  background: rgba(236, 72, 153, 0.06);
  box-shadow: 0 4px 16px rgba(236, 72, 153, 0.12);
}

.role:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.role-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  width: 100%;
}

.role-emoji {
  font-size: 36px;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}

.role-body {
  flex: 1;
  min-width: 0;
}

.role-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 5px;
}

.role-name {
  font-size: 16px;
  font-weight: 700;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.75);
}

.role-pill {
  font-size: 11px;
  color: var(--muted);
  border: 1px solid var(--card-border);
  padding: 3px 8px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.65);
}

.role-pill.pill-active {
  color: var(--accent-a);
  border-color: rgba(236, 72, 153, 0.32);
  background: rgba(236, 72, 153, 0.1);
}

.role-desc {
  margin: 0 0 4px;
  font-size: 14px;
  color: var(--text);
  font-weight: 500;
  text-shadow: 0 0 6px rgba(255, 255, 255, 0.7);
}

.role-flavor {
  margin: 0;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.55;
  text-shadow: 0 0 6px rgba(255, 255, 255, 0.65);
}

.check-mark {
  width: 20px;
  height: 20px;
  color: var(--accent-a);
  flex-shrink: 0;
  margin-top: 2px;
}

.check-mark svg {
  width: 100%;
  height: 100%;
}
</style>
